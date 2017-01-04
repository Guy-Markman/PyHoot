
import base
import util

CLOSE, SERVER, ACTIVE = range(3)


class Disconnect(RuntimeError):

    def __init__(self):
        super(Disconnect, self).__init__("Disconnect")


class Server(base.Base):
    _datbase = {}

    def __init__(
        self,
        buff_size,
    ):
        super(Server, self).__init__()
        self._buff_size = buff_size
        self._run = True
        self.logger.info("buff size %d" % buff_size)

    def add_server(
        self,
        our_address=("localhost", 80)
    ):
        s = util.creat_nonblocking_socket()
        s.setnonblocking(0)
        s.listen(1)
        self._add_to_database(s, state=SERVER)

    def _add_to_database(self, socket, state=ACTIVE):
        self._database[socket.fileno()] = {
            "socket": socket,
            "buff": "",
            "state": state,
        }
