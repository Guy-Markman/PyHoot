# TODO: switch use of dictionary to Client object
import errno
import select
import socket
import traceback

import base
import Client
import util

CLOSE, SERVER, CLIENT = range(3)
CRLF = "\r\n"
END_HEARDER = 2 * CRLF
HTTP_VERSION = "HTTP/1.1"
MAX_NUMBER_OF_HEADERS = 100


class Disconnect(RuntimeError):

    def __init__(self):
        super(Disconnect, self).__init__("Disconnect")


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
        self.logger.info("Initialized server, buff size %d" % buff_size)
        self._base_directory = base_directory
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
    #            "state": state of the socket, CLOSE, SERVER or CLIENT,
    #            "file": file_object to send,
    #            "peer": CLIENT, the server we are connected to,
    #                    SERVER, list of the sockets that connected to server
    #                    CLOSE, None
    #            }
    def _add_to_database(self, socket, state=CLIENT, peer=None):
        if state not in (CLOSE, SERVER, CLIENT):
            raise RuntimeError("State not found")
        self._database[socket] = {
            "state": state,
        }
        if state == SERVER:
            self._database[socket]["peer"] = {}
        elif state == CLIENT:
            self._database[socket]["client"] = Client.Client(socket, peer)
        else:
            self._database[socket]["peer"] = None
        self.logger.debug("Socket added to database, {%s: %s}" % (
            socket,
            self._database[socket]
        ))

    # close the socket, remove it from it's from the database and remove
    # references to it from it's peer
    def _close_socket(self, socket):
        entry = self._database[socket]
        if entry["peer"] is not None:
            self._remove_refernces(entry)

        socket.close()
        self._database.pop(socket)
        self.logger.debug("Close success")

    def _change_to_close(self, socket):
        self.datbase[socket]["state"] = CLOSE
        self._remove_refernces(socket)

    # Remove refences from database
    def _remove_refernces(self, socket):
        entry = self._database[socket]
        if entry["state"] == CLIENT:
            self._database[self._database[socket]["peer"]].pop(socket)
        elif entry["state"] == SERVER:
            for peer_socket in self._database[socket]["peer"].keys():
                peer_database = self._database[peer_socket]
                peer_database["peer"] = None
                peer_database.pop("client")

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
            if entry["state"] == CLIENT:
                if entry:
                    wlist.append[socket]
                socket_peer = entry["client"].get_peer()
                if (
                    self._datbase[socket_peer]["peer"]
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
            self._add_to_database(socket=socket, state=CLIENT, peer=socket)
            self._database[socket]["peer"].append(accepted)
            self.logger.info("connect the socket from %s" % addr)
        except Exception:
            self.loggger.error(traceback.format_exc)
            if accepted is not None:
                accepted.close()

    # Creat the error we will send to the client
    def _creat_error(self, s, code, message, extra):
        self._database[s]["buff"] = (
            """%s %s %s \r\n
                Content-Length: %s\r\n
                \r\n
                %s""" % (
                HTTP_VERSION,
                code,
                message,
                code,
                message,
                extra
            )
        )

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
                    socket_state = self._database[socket]["state"]
                    if socket_state == SERVER:
                        self._connect_socket(s)
                    elif socket_state == CLIENT:
                        self._handle_CLIENT(s)
                for s in xlist:
                    raise RuntimeError("Error in socket, closing it")

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
