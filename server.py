import errno
import select
import socket
import traceback

from . import async_io, base, client, common_events, constants, custom_exceptions, util


class Server(base.Base):

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

    def _add_to_databases(self, s, state=constants.SERVER):
        """
                Add the socket to the database, structre will be:
                {socket :  {
                "buff":buffer will contain the data we need to send,
                "state": state of the socket, CLOSE, SERVER or CLIENT,
                "fd": file descriptor of the socket
                }
        """
        if state not in (constants.CLOSE, constants.SERVER, constants.CLIENT):
            raise RuntimeError("State not found")
        self._database[s] = {
            "buff": "",
            "state": state,
            "fd": s.fileno(),
        }
        entry = self._database[s]
        if state == constants.CLIENT:
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
        if entry["state"] == constants.CLIENT:
            entry["buff"] = entry["client"].get_send_buff()
            if entry["client"].get_file() is not None:
                entry["client"].get_file().close()
            entry.pop("client")
        entry["state"] = constants.CLOSE

    def _connect_socket(self, server):
        """accept socket to the system and add it to the database
        """
        accepted = None
        try:
            accepted, addr = server.accept()
            accepted.setblocking(0)
            self._add_to_databases(accepted, state=constants.CLIENT)
            self.logger.info("connect the socket from '%s:%s'", *addr)
        except Exception:
            self.logger.error("Exception ", exc_info=True)
            if accepted is not None:
                accepted.close()

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
                    if entry["state"] == constants.CLIENT:
                        if entry["client"].check_finished_request():
                            self.logger.info("Finished Request for %s" % s)
                            self._change_to_close(s)
                    if entry["state"] == constants.CLOSE:
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
                        if socket_state == constants.SERVER:
                            self.logger.debug("Server read")
                            self._connect_socket(s)
                        elif socket_state == constants.CLIENT:
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
                        if entry["state"] == constants.CLIENT:
                            self.logger.debug("Client send")
                            entry["client"].send()
                            if entry["client"].check_finished_request():
                                self.logger.info("Finished Request for %s" % s)
                                self._change_to_close(s)
                        if entry["state"] == constants.CLOSE:
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
