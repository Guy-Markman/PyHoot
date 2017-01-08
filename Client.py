
class Client(base.Base):
    def __init__(
        socket,
        buff,
        peer,
        file = None,
        Request = None
    ):
        self._socket = socket
        self.buff = buff
        self._peer = peer
        self.file = file
        self.Request = Request
    
    def get_socket():
        return self._socket
    
    def get_peer():
        return self._peer