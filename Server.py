import errno
import select
import socket
import traceback

from . import async_io, base, client, common_events, custom_exceptions, util


class Server(base.Base):
    CLOSE, SERVER, CLIENT = range(3)
    _database = {}
    _fd_socket = {}

    def __init__(
        self,
        buff_size,
        base_directory,
        io_mode
    ):
        super(Server, self).__init__()
        self._buff_size = buff_size
        self._async_io_object = async_io.AsyncIO(io_mode)
        self._run = True
        self.logger.info("Initialized server, buff size '%d'", buff_size)
        self._base_directory = base_directory

    def terminate(self):
        self._run = False

    def add_server(
        self,
        our_address=("localhost", 80)
    ):
        """ Creat server side socket and add it to the database. \n
            our_address: tupple of the address that the server will do bind to.
                         format (address, port), default (localhost, 80)
        """
        s = util.creat_nonblocking_socket()
        s.bind(our_address)
        s.listen(1)
        self._add_to_databases(s)
        self.logger.info("Created server on address %s:%s", *our_address)

    def _add_to_databases(self, s, state=SERVER):
        """
                Add the socket to the database, structre will be:
                {socket :  {
                "buff":buffer will contain the data we need to send,
                "state": state of the socket, CLOSE, SERVER or CLIENT,
                "fd": file descriptor of the socket
                }
        """
        if state not in (self.CLOSE, self.SERVER, self.CLIENT):
            raise RuntimeError("State not found")
        self._database[s] = {
            "buff": "",
            "state": state,
            "fd": s.fileno(),
        }
        entry = self._database[s]
        if state == self.CLIENT:
            entry["client"] = client.Client(
                s, self._buff_size, self._base_directory)
        self._fd_socket[s.fileno()] = s
        self.logger.debug(
            "s added to database, {'%s': '%s'}",
            s,
            self._database[s])

    def _close_socket(self, s):
        """ close the socket, remove it from it's from the database"""
        s.close()
        self._database.pop(s)
        self.logger.debug("Close success on socket %s", s)

    def _change_to_close(self, s):  # TODO: pass entry
        """Change the socket s to close state"""
        entry = self._database[s]
        self.logger.debug("Current entry %s", entry)
        if entry["state"] == self.CLIENT:
            entry["buff"] = entry["client"].get_send_buff()
            if entry["client"].get_file() is not None:
                entry["client"].get_file().close()
            entry.pop("client")
        entry["state"] = self.CLOSE

    def _connect_socket(self, server):
        """accept socket to the system and add it to the database
        """
        accepted = None
        try:
            accepted, addr = server.accept()
            accepted.setblocking(0)
            self._add_to_databases(accepted, state=self.CLIENT)
            self.logger.info("connect the socket from '%s:%s'", *addr)
        except Exception:
            self.logger.error("Exception ", exc_info=True)
            if accepted is not None:
                accepted.close()

    def _build_select(self):
        """build the three list (rlist, wlist, xlist) for select.select"""
        rlist = []
        wlist = []
        xlist = []
        for s in self._database.keys():
            entry = self._database[s]
            if entry["state"] == self.CLOSE:
                wlist.append(s)
            if entry["state"] == self.SERVER:
                rlist.append(s)
            if entry["state"] == self.CLIENT:
                cl = entry["client"]
                if cl.can_recv():
                    rlist.append(s)
                if cl.can_send():
                    wlist.append(s)
        self.logger.debug(
            "build select\n rlist %s\nwlist %s\n xlist %s",
            rlist, wlist, xlist
        )
        return rlist, wlist, xlist

    def _io_select(self):
        """Build select and use it"""
        rlist, wlist, xlist = self._build_select()
        return select.select(rlist, wlist, xlist)

    def _select_to_poll(self):
        """Turn the results of a select into the format of poll"""
        rlist, wlist, xlist = self._io_select()
        self.logger.debug(
            "select to poll \n rlist %s\nwlist %s\n xlist %s",
            rlist, wlist, xlist
        )
        polled = {}
        for s in rlist + wlist + xlist:
            fd = self._database[s]["fd"]
            if s in rlist:
                polled[fd] = common_events.CommonEvents.POLLIN
            if s in wlist:
                polled[fd] = common_events.CommonEvents.POLLOUT
            if s in xlist:
                polled[fd] = common_events.CommonEvents.POLLERR
        events = polled.items()
        return events

    def _build_poller(self):
        """Creat and register poll"""
        poller = select.poll()
        for entry in self._database.values():
            events = common_events.CommonEvents.POLLERR
            if entry["state"] == self.CLOSE:
                events |= common_events.CommonEvents.POLLOUT
            elif entry["state"] == self.SERVER:
                events |= common_events.CommonEvents.POLLIN
            elif entry["state"] == self.CLIENT:
                cl = entry["client"]
                if cl.can_recv():
                    events |= common_events.CommonEvents.POLLIN
                if cl.can_send():
                    events |= common_events.CommonEvents.POLLOUT
            self.logger.debug(
                "reistered %s with events %s",
                entry["fd"],
                events)
            poller.register(entry["fd"], events)
        return poller

    def _io_poller(self):
        """Build poll and use it"""
        return self._build_poller().poll()

    def start_server(self):
        """The main function of the class, makes everything work"""
        while self._database:
            try:
                # check if the program need to stop, if it does starts the
                # process of shuting down everything by changing all the states
                # to close
                if not self._run:
                    self.logger.debug("closing all")
                    for s in self._database.keys():
                        self._change_to_close(s)

                # closing every socket that is ready for close (sent everything
                # and in close mode)
                for s in self._database.keys():
                    entry = self._database[s]
                    if entry["state"] == self.CLIENT:
                        if entry["client"].check_finished_request():
                            self.logger.info("Finished Request for %s" % s)
                            self._change_to_close(s)
                    if entry["state"] == self.CLOSE:
                        if entry["buff"] == "":
                            self._close_socket(s)

                self._async_io_object.creat_object()
                events = self._async_io_object.poll()
                self.logger.debug("Events \n%s", events)
                for fd, flag in events:
                    # taking care of all the sockets in rlist
                    s = self._fd_socket[fd]
                    if flag & common_events.CommonEvents.POLLIN:
                        socket_state = self._database[s]["state"]
                        if socket_state == self.SERVER:
                            self.logger.debug("Server read")
                            self._connect_socket(s)
                        elif socket_state == self.CLIENT:
                            self.logger.debug("Client Read")
                            self._database[s]["client"].recv()
                            self.logger.debug("finished reciving")

                    if flag & common_events.CommonEvents.POLLHUP:
                        raise custom_exceptions.Disconnect()

                    if flag & common_events.CommonEvents.POLLERR:
                        raise RuntimeError(
                            "Error in socket %s , closing it", s)

                    if flag & common_events.CommonEvents.POLLOUT:
                        entry = self._database[s]
                        if entry["state"] == self.CLIENT:
                            self.logger.debug("Client send")
                            entry["client"].send()
                            if entry["client"].check_finished_request():
                                self.logger.info("Finished Request for %s" % s)
                                self._change_to_close(s)
                        if entry["state"] == self.CLOSE:
                            self.logger.debug("Close send")
                            self.send(s)

            # taking care of errors
            except select.error as e:
                if e[0] != errno.EINTR:
                    self.logger.error(traceback.format_exc())
                    self._close_socket(s)
            except custom_exceptions.Disconnect:
                self.logger.info("%s Disconneted", s)
                self._close_socket(s)
            except Exception:
                self.logger.critical(traceback.format_exc())
                self._close_socket(s)
        self.logger.debug("Finishing")
        self.logger.debug(self._database)

    def send(self, s):
        while self._database[s]["buff"]:
            try:
                sent = s.send(self._database[s]["buff"])
                self.logger.debug("sent %s" % sent)
                self._database[s]["buff"] = self._database[s]["buff"][sent:]
            except socket.error as e:
                self.logger.error(traceback.format_exc())
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                else:
                    self.logger.debug("ERROR WOULD BLOCK")
                    break
        self.logger.debug("left %s" % len(self._database[s]["buff"]))
