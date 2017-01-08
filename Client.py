import errno
import socket

import base
import util


class Client(base.Base):
    """Client of Server, handle everything by itself"""

    def __init__(
        self,
        s,
        file=None,
        request=None
    ):
        """
        Client of Server, handle everything by itself
        Arguements:
        s: the socket of this client, CANNOT BE MODIFIED
        buff: Every data we recv from the client and had not been procssed
              (mostly partial lines)
        """
        self._socket = s
        self.buff = ""
        self.file = file
        self.request = request

    def get_socket(self):
        """Get the socket of this client, private arguement"""
        return self._socket

    def read(self):
        if self.request is None:
            try:
                util.recv_line(self.s, self.buff)
            except socket.error as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
