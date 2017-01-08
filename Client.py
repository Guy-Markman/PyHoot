import base


class Client(base.Base):

    def __init__(
        self,
        socket,
        peer,
        buff="",
        file=None,
        request=None
    ):
        self._socket = socket
        self.buff = buff
        self._peer = peer
        self.file = file
        self.request = request

    def get_socket(self):
        return self._socket

    def get_peer(self):
        return self._peer
