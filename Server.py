import errno
import os
import select
import socket
import traceback

import base
import Client
import CustomExceptions
import util
from common_events import CommonEvents

CLOSE, SERVER, CLIENT = range(3)


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
        self._io_function = (
            self._select_to_poll if io_mode == "select" else
            self._io_poller
        )
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

    def _add_to_databases(self, s, state=SERVER):
        """
                Add the socket to the database, structre will be:
                {socket :  {
                "buff":buffer will contain the data we need to send,
                "state": state of the socket, CLOSE, SERVER or CLIENT,
                "fd": file descriptor of the socket
                }
        """
        if state not in (CLOSE, SERVER, CLIENT):
            raise RuntimeError("State not found")
        self._database[s] = {
            "state": state,
            "fd": s.fileno(),
        }
        entry = self._database[s]
        if state == CLIENT:
            entry["client"] = Client.Client(s, self._buff_size)
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

    def _change_to_close(self, s):
        """Change the socket s to close state"""
        if s in self._database.keys():
            entry = self._database[s]
            self.logger.debug("Current entry %s", entry)
            if entry["state"] == CLIENT:
                entry["buff"] = entry["client"].get_send_buff()
                if entry["client"].get_file() is not None:
                    entry["client"].get_file().close()
                entry.pop("client")
            elif entry["state"] == SERVER:
                entry["buff"] = ""
            entry["state"] = CLOSE

    def _build_select(self):
        """build the three list (rlist, wlist, xlist) for select.select"""
        rlist = []
        wlist = []
        xlist = []
        for s in self._database.keys():
            if self._database[s]["state"] != CLOSE:
                rlist.append(s)
            wlist.append(s)
            xlist.append(s)
        return rlist, wlist, xlist

    def _connect_socket(self, server):
        """accept socket to the system and add it to the database
        """
        accepted = None
        try:
            accepted, addr = server.accept()
            accepted.setblocking(0)
            self._add_to_databases(accepted, state=CLIENT)
            self.logger.info("connect the socket from '%s:%s'", *addr)
        except Exception:
            self.logger.error("Exception ", exc_info=True)
            if accepted is not None:
                accepted.close()

    def _io_select(self):
        """Build select and use it"""
        return select.select(*self._build_select())

    def _build_poller(self):
        """Creat and register poll"""
        poller = select.poll()
        for entry in self._database.values():
            events = CommonEvents.POLLERR
            if entry["state"] == CLOSE:
                events |= CommonEvents.POLLOUT
            elif entry["state"] == SERVER:
                events |= CommonEvents.POLLIN
            elif events["state"] == CLIENT:
                cl = entry["client"]
                if cl.can_recv():
                    events |= CommonEvents.POLLIN
                if cl.can_send():
                    events |= CommonEvents.POLLOUT
            self.logger.debug("reistered %s with events %s", entry["socket"])
            poller.register(entry["fd"], events)
        return poller

    def _select_to_poll(self):
        """Turn the results of a select into the format of poll"""
        rlist, wlist, xlist = self._io_select()
        polled = {}
        for s in rlist + wlist + xlist:
            fd = s.fileno()
            if s in rlist:
                polled[fd] = CommonEvents.POLLIN
            if s in wlist:
                polled[fd] = CommonEvents.POLLOUT
            if s in xlist:
                polled[fd] = CommonEvents.POLLERR
        events = polled.items()
        return events

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
                    if entry["state"] == CLIENT:
                        if entry["client"].check_finished_request():
                            self.logger.info("Finished Request for %s" % s)
                            self._change_to_close(s)
                    if entry["state"] == CLOSE:
                        if entry["buff"] == "":
                            self._close_socket(s)

                # build and do select
                # TODO: Implemnt the io-s and change the format down here
                rlist, wlist, xlist = self._build_select()
                if (rlist or wlist or xlist):
                    rlist, wlist, xlist = select.select(rlist, wlist, xlist)
                    self.logger.debug("""After select\n
                                         rlist = '%s'\n
                                         wlist = '%s'\n
                                         xlist = '%s'\n
                                      """ % (rlist, wlist, xlist))
                    # taking care of all the sockets in rlist
                    for s in rlist:
                        socket_state = self._database[s]["state"]
                        if socket_state == SERVER:
                            self.logger.debug("Server read")
                            self._connect_socket(s)
                        elif socket_state == CLIENT:
                            self.logger.debug("Client Read")
                            self._database[s]["client"].recv()
                            self.logger.debug("finished reciving")
                    for s in wlist:
                        entry = self._database[s]
                        if entry["state"] == CLIENT:
                            self.logger.debug("Client send")
                            entry["client"].send()
                            if entry["client"].check_finished_request():
                                self.logger.info("Finished Request for %s" % s)
                                self._change_to_close(s)
                        if entry["state"] == CLOSE:
                            self.logger.debug("Close send")
                            self.send(s)
                    for s in xlist:
                        raise RuntimeError(
                            "Error in socket %s , closing it", s)

            # taking care of errors
            except select.error as e:
                if e[0] != errno.EINTR:
                    self.logger.error(traceback.format_exc())
                    self._close_socket(s)
            except CustomExceptions.Disconnect:
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
