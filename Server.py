import errno
import select
import traceback

import base
import util

CLOSE, SERVER, ACTIVE = range(3)


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

    def add_server(
        self,
        our_address=("localhost", 80)
    ):
        s = util.creat_nonblocking_socket()
        s.setnonblocking(0)
        s.listen(1)
        self._add_to_database(s, state=SERVER)
        self.logger.info("Created server on address %s" % our_address)

    def _add_to_database(self, socket, state=ACTIVE, peer=None):
        if state not in (CLOSE, SERVER, ACTIVE):
            raise RuntimeError("Type not found")
        self._database[socket] = {
            "fd": socket.fileno(),
            "buff": "",
            "state": state,
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

    def _build_select(self):
        rlist = []
        wlist = []
        xlist = []
        for socket in self._database.keys():
            xlist.append[socket]
            entry = self._database[socket]
            if entry["state"] == CLOSE:
                wlist.append[socket]
            if entry["state"] == SERVER:
                rlist.append[socket]
            if entry["state"] == ACTIVE:
                if entry["buff"]:
                    wlist.append[socket]
                fd_peer = entry["peer"]
                if (
                    fd_peer is not None
                    and len(self._database[fd_peer]) < self._buff_size
                ):
                    rlist.append[socket]
        return rlist, wlist, xlist

    def start_server(self):
        while self._database:
            try:
                if not self._run:
                    self.logger.info("closing all")
                    for entry in self._database:
                        entry["state"] = CLOSE

                for socket in self._database.keys():
                    entry = self._database[socket]
                    if entry["state"] == CLOSE and entry["buff"] == "":
                        self.logger.info("closing socket, fd %d" %
                                         entry[socket.fileno()])
                        self._close_socket(socket)
                rlist, wlist, xlist = select.select(self._build_select())
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
