# TODO: write file object
import errno
import select
import socket
import traceback

import base
import util

CLOSE, SERVER, ACTIVE = range(3)
CRLF = "\r\n"
END_HEARDER = 2 * CRLF


class Disconnect(RuntimeError):

    def __init__(self):
        super(Disconnect, self).__init__("Disconnect")


class Server(base.Base):
    _database = {}

    def __init__(
        self,
        buff_size,
    ):
        super(Server, self).__init__()
        self._buff_size = buff_size
        self._run = True
        self.logger.info("Initialized server, buff size %d" % buff_size)

    # Creat server side socket and add it to the database. \n
    # our_address: tupple of the address that the server will do bind to.
    #              format (address, port), default (localhost, 80)
    def add_server(
        self,
        our_address=("localhost", 80)
    ):
        s = util.creat_nonblocking_socket()
        s.setnonblocking(0)
        s.listen(1)
        self._add_to_database(s, state=SERVER)
        self.logger.info("Created server on address %s" % our_address)

    # Add the socket to the database, structre will be:
    # {socket :  {
    #            "buff":buffer will contain the data we need to send,
    #            "state": state of the socket, CLOSE, SERVER or ACTIVE,
    #            "file": file_object to send,
    #            "peer": ACTIVE, the server we are connected to,
    #                    SERVER, list of the sockets that connected to server
    #                    CLOSE, None
    #            }
    def _add_to_database(self, socket, state=ACTIVE, peer=None):
        if state not in (CLOSE, SERVER, ACTIVE):
            raise RuntimeError("State not found")
        self._database[socket] = {
            "buff": "",
            "state": state,
            "file": None
        }
        if state == SERVER:
            self._database[socket].update({"peer": []})
        elif state == ACTIVE:
            self._database[socket].update({"peer": peer})
        else:
            self._database[socket].update({"peer": None})
        self.logger.debug("Socket added to database, {%s: %s}" % (
            socket,
            self._database[socket]
        ))

    # close the socket, remove it from it's from the database and remove
    # references to it from it's peer
    def _close_socket(self, socket):
        entry = self._database[socket]
        peer_socket = entry["peer"]
        if peer_socket is not None:
            if entry["state"] == ACTIVE:
                self._database[peer_socket].remove(socket)
            elif entry["state"] == SERVER:
                for peer_socket in self._database[socket]["peer"]:
                    peer_database = self._database[peer_socket]
                    peer_database.update({
                        "peer": None,
                        "state": CLOSE
                    })

        socket.close()
        self._database.pop(socket)
        self.logger.debug("Close success")

    # build the three list (rlist, wlist, xlist) for select.select
    def _build_select(self):
        rlist = []
        wlist = []
        xlist = []
        for s in self._database.keys():
            xlist.append[socket]
            entry = self._database[socket]
            if entry["state"] == CLOSE:
                wlist.append[socket]
            if entry["state"] == SERVER:
                rlist.append[socket]
            if entry["state"] == ACTIVE:
                if entry["buff"]:
                    wlist.append[socket]
                socket_peer = entry["peer"]
                if (
                    socket_peer is not None
                    and (len(self._database[socket_peer]["buff"]) <
                         self._buff_size)
                ):
                    rlist.append[socket]
        self.logger.debug("""rlist = %s\n
                             wlist = %s\n
                             xlist = %s\n
                          """ % (rlist, wlist, xlist))
        return rlist, wlist, xlist

    # accept socket to the system, add it to the database and add reference to
    # it in the server it's connect to
    def _connect_socket(self, socket):
        accepted = None
        try:
            accepted, addr = socket.accept()
            accepted.setblocking(0)
            self._add_to_database(socket=socket, state=ACTIVE, peer=socket)
            self._database[socket]["peer"].append(accepted)
            self.logger.info("connect the socket from %s" % addr)
        except Exception:
            self.loggger.error(traceback.format_exc)
            if accepted is not None:
                accepted.close()

    # The main function of the class, makes everything work
    def start_server(self):
        while self._database:
            try:
                # check if the program need to stop, if it does starts the
                # process of shuting down everything by changing all the states
                # to close
                if not self._run:
                    self.logger.info("closing all")
                    for entry in self._database:
                        entry["state"] = CLOSE
                        entry["peer"] = None

                # closing every socket that is ready for close (sent everything
                # and in close mode)
                for s in self._database.keys():
                    entry = self._database[socket]
                    if entry["state"] == CLOSE and entry["buff"] == "":
                        self.logger.info("closing socket, fd %d" %
                                         entry[socket.fileno()])
                        self._close_socket(s)

                # build and do select
                rlist, wlist, xlist = select.select(self._build_select())
                # taking care of all the sockets in rlist
                for s in rlist:
                    if self._database[socket]["state"] == SERVER:
                        self._connect_socket(s)
                    else:
                        while True:
                            try:
                                self._database[s]["buff"] += util.recv_line(
                                    s,
                                    self._database[s]["buff"],
                                    block_size=self._buff_size)
                            except socket.error as e:
                                if e.errno not in (errno.EWOULDBLOCK,
                                                   errno.EAGAIN):
                                    raise
                                break
                        if END_HEARDER in self._database[s]["buff"]:
                            print "TODO"
                            # TODO: Continue writing it

            # taking care of errors
            except select.error as e:
                if e[0] != errno.EINTR:
                    self.logger.error(traceback.format_exc())
                    self._close_socket(socket)
            except Disconnect as e:
                self._close_socket(socket)
                self.logger.error(traceback.format_exc())
            except Exception as e:
                self._close_fd(socket)
                self.logger.critical(traceback.format_exc)
