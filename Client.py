import os.path
import traceback

import base
import constants
import FileObject
import Request
import util

SUPPORTED_METHODS = ('GET')


class Client(base.Base):
    """Client of Server, handle everything by itself"""

    def __init__(
        self,
        s,
        buff_size,
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
        super(Client, self).__init__()
        self._socket = s
        self.buff = ""
        self._buff_size = buff_size
        self.file = file
        self.request = request

    def get_socket(self):
        """Get the socket of this client, private arguement"""
        return self._socket

    def read(self):
        try:
            if self.request is None or constants.CRLF not in self.buff:
                self.buff += util.recv_line(self._socket)
            if self.request is None:
                if constants.CRLF in self.buff:
                    req = self.buff.split(' ', 2)
                    if req[2] != constants.HTTP_VERSION:
                        raise RuntimeError('Not HTTP protocol')
                    if len(req) != 3:
                        raise RuntimeError('Incomplete HTTP protocol')
                    method, uri, signature = req
                    if method not in SUPPORTED_METHODS:
                        raise RuntimeError(
                            "HTTP unspported method '%s'" % method)
                    if not uri or uri[0] != '/' or '\\' in uri:
                        raise RuntimeError("Invalid URI")
                    file_name = os.path.normapth(
                        '%s%s' % (constants.base, os.path.normpath(uri)))
                    self.file = FileObject.FileObject(
                        file_name, self._buff_size)
                    self.request = Request.Request(method, uri)
                    self.buff = ""
            if self.request is not None:
                while True:
                    buf = util.recv_line(self._socket)
                    if not buf:
                        break
                    self.buff += buf
                    lines = self.buff.split(constants.CRLF)
                    for line in lines[:-1]:
                        self.request.add_header(*line.split(": ", 2))
                    if ": " in line[-1]:
                        self.request.add_header(*line.split(": ", 2))
                        self.buff = ""
                    else:
                        self.buff = line[-1]
        except Exception as e:
            self.logger.error(traceback.format_exc)
            self.buff = util.creat_error(500, "Internal Error", e)
            raise e
