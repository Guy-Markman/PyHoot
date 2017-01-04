import base


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
