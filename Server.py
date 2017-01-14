import errno
import select
import socket
import traceback

import base
import Client
import CustomExceptions
import util

CLOSE, SERVER, CLIENT = range(3)
CRLF = "\r\n"
END_HEARDER = 2 * CRLF


class Server(base.Base):
    _database = {}

    def __init__(
        self,
        buff_size,
        base_directory
    ):
        super(Server, self).__init__()
        self._buff_size = buff_size
        self._run = True
        self.logger.info("Initialized server, buff size '%d'" % buff_size)
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
        self._add_to_database(s)
        self.logger.info("Created server on address '%s:%s'" % our_address)

    def _add_to_database(self, s, state=SERVER, peer=None):
        """
                Add the socket to the database, structre will be:
                {socket :  {
                "buff":buffer will contain the data we need to send,
                "state": state of the socket, CLOSE, SERVER or CLIENT,
                "file": file_object to send,
                "peer": CLIENT, the server we are connected to,
                        SERVER, list of the sockets that connected to server
                        CLOSE, None
                }
        """
        if state not in (CLOSE, SERVER, CLIENT):
            raise RuntimeError("State not found")
        self._database[s] = {
            "state": state,
        }
        entry = self._database[s]
        if state == SERVER:
            entry["peer"] = []
        elif state == CLIENT:
            entry["client"] = Client.Client(s, self._buff_size)
            entry["peer"] = peer
        else:
            self._database[s]["peer"] = None
        self.logger.debug("s added to database, {'%s': '%s'}" % (
            s,
            self._database[s]
        ))

    def _close_socket(self, s):
        """ close the socket, remove it from it's from the database and remove
        references to it from it's peer"""
        self.logger.debug(self._database)
        s.close()
        self._database.pop(s)
        self.logger.debug("Close success")

    def _change_to_close(self, s):
        """Change the socket s to close state"""
        if s in self._database.keys():
            entry = self._database[s]
            if entry["state"] == CLIENT:
                self.logger.debug(entry)
                if (entry["peer"] is not None and
                        entry["peer"] in self._database.keys()):
                    self._database[entry["peer"]]["peer"].remove(s)
                entry["peer"] = None
                entry["buff"] = entry["client"].get_send_buff()
                entry.pop("client")
            elif entry["state"] == SERVER:
                self.logger.debug(self._database)
                for peer_s in self._database[s]["peer"]:
                    self.logger.debug(peer_s)
                    self._change_to_close(peer_s)
                entry["buff"] = ""
            entry["state"] = CLOSE

    def _build_select(self):
        """build the three list (rlist, wlist, xlist) for select.select"""
        rlist = []
        wlist = []
        xlist = []
        for s in self._database.keys():
            xlist.append(s)
            entry = self._database[s]
            if entry["state"] == CLOSE:
                wlist.append(s)
            if entry["state"] == SERVER:
                rlist.append(s)
            if entry["state"] == CLIENT:
                if entry["client"].can_send():
                    wlist.append(s)
                if entry["client"].can_recv():
                    rlist.append(s)
        self.logger.debug("""rlist = '%s'\n
                             wlist = '%s'\n
                             xlist = '%s'\n
                          """ % (rlist, wlist, xlist))
        return rlist, wlist, xlist

    def _connect_socket(self, server):
        """accept socket to the system, add it to the database and add referene
           to it in the server it's connect to
        """
        accepted = None
        try:
            accepted, addr = server.accept()
            accepted.setblocking(0)
            self._add_to_database(accepted, state=CLIENT, peer=server)
            self._database[server]["peer"].append(accepted)
            self.logger.info("connect the socket from '%s:%s'" % addr)
        except Exception:
            self.logger.error(traceback.format_exc())
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
                    self.logger.info("closing all")
                    for s in self._database.keys():
                        self._change_to_close(s)

                # closing every socket that is ready for close (sent everything
                # and in close mode)
                for s in self._database.keys():
                    entry = self._database[s]
                    if entry["state"] == CLOSE:
                        if entry["buff"] == "":
                            self._close_socket(s)

                # build and do select
                rlist, wlist, xlist = self._build_select()
                if (rlist or wlist or xlist):
                    rlist, wlist, xlist = select.select(rlist, wlist, xlist)
                    self.logger.debug("Passed select")
                    self.logger.debug("""rlist = '%s'\n
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
                        if entry["state"] == CLOSE:
                            self.logger.debug("Close send")
                            self.send(s)

                    for s in xlist:
                        raise RuntimeError("Error in socket, closing it")

            # taking care of errors
            except select.error as e:
                if e[0] != errno.EINTR:
                    self.logger.error(traceback.format_exc())
                    self._close_socket(s)
            except CustomExceptions.Disconnect:
                self.logger.error(traceback.format_exc())
                self._close_socket(s)
            except CustomExceptions.FinishedRequest:
                self.logger.info("Finished Request for %s" % s)
                self._change_to_close(s)
            except Exception:
                self.logger.critical(traceback.format_exc())
                self._close_socket(s)
        self.logger.debug("Finishing")
        self.logger.debug(self._database)

    def send(self, s):
        self.logger.debug(self._database[s])
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
                    break
        self.logger.debug("left %s" % len(self._database[s]["buff"]))
