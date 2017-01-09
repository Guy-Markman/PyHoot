# TODO: switch use of dictionary to Client object
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

    def add_server(
        self,
        our_address=("localhost", 80)
    ):
        """ Creat server side socket and add it to the database. \n
            our_address: tupple of the address that the server will do bind to.
                         format (address, port), default (localhost, 80)
        """
        s = util.creat_nonblocking_socket()
        s.setnonblocking(0)
        s.listen(1)
        self._add_to_database(s)
        self.logger.info("Created server on address '%s'" % our_address)
        self._ad

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
        if self._database[s]["state"] != CLOSE:
            self._change_to_close(s)
        s.close()
        self._database.pop(s)
        self.logger.debug("Close success")

    def _change_to_close(self, s):
        """Change the socket s to close state"""
        entry = self._database[s]
        entry["state"] = CLOSE
        if entry["state"] == CLIENT:
            if entry["peer"] is not None:
                self._database[entry["peer"]].pop(s)
            entry["buff"] = entry["client"].get_send_buff()
            entry["peer"] = None
            entry.pop("client")
        elif entry["state"] == SERVER:
            for peer_s in self._database[s]["peer"].keys():
                peer_s._change_to_close(peer_s)

    def _build_select(self):
        """build the three list (rlist, wlist, xlist) for select.select"""
        rlist = []
        wlist = []
        xlist = []
        for s in self._database.keys():
            xlist.append[s]
            entry = self._database[s]
            if entry["state"] == CLOSE:
                wlist.append[s]
            if entry["state"] == SERVER:
                rlist.append[s]
            if entry["state"] == CLIENT:
                if entry:
                    wlist.append[s]
                if self._database[s]["client"].buff:
                    rlist.append[s]
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
            self.logger.info("connect the socket from '%s'" % addr)
        except Exception:
            self.loggger.error(traceback.format_exc)
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
                    if entry["state"] == CLOSE and entry["buff"] == "":
                        self._close_socket(s)

                # build and do select
                rlist, wlist, xlist = select.select(self._build_select())
                # taking care of all the sockets in rlist
                for s in rlist:
                    socket_state = self._database[socket]["state"]
                    if socket_state == SERVER:
                        self._connect_socket(s)
                    elif socket_state == CLIENT:
                        self._database[s]["client"].read()
                for s in xlist:
                    raise RuntimeError("Error in socket, closing it")

            # taking care of errors
            except select.error as e:
                if e[0] != errno.EINTR:
                    self.logger.error(traceback.format_exc())
                    self._close_socket(s)
            except CustomExceptions.Disconnect as e:
                self._close_socket(s)
                self.logger.error(traceback.format_exc())
            except CustomExceptions.FinishedRequest as e:
                self._database[s]["client"] = Client.Client(
                    s, self._buff_size)
            except Exception as e:
                self._close_socket(s)
                self.logger.critical(traceback.format_exc)
