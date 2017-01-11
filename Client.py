import errno
import os.path
import socket
import traceback

import base
import constants
import CustomExceptions
import FileObject
import Request
import util

SUPPORTED_METHODS = ('GET')

MIME_MAPPING = {
    'html': 'text/html',
    'png': 'image/png',
    'txt': 'text/plain',
}


class Client(base.Base):
    """ Client of Server, handle everything by itself
        Variables:
                self._socket = The socket of the client
                self._recv_buff = any data we recieved but hadn't procssed yet
                self._send_buff = All the data that needed to be sent but
                                  hadn't sent yet
                self._buff_size = The buff size of the server
                self.file = FileObject of the file the request wants
                self.request = Request object of the request we got
    """

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
        _recv_buff: Every data we recv from the client and had not been
                    procssed (mostly partial lines)
        _send_buff: Every data we need to send but didn't sent yet
        """
        super(Client, self).__init__()
        self._socket = s
        self._recv_buff = ""
        self._send_buff = ""
        self._buff_size = buff_size
        self.file = file
        self.request = request

    def get_socket(self):
        """Get the socket of this client, private arguement"""
        return self._socket

    def recv(self):
        """Recv data from the client socket and process it to Reqeust and
           FileObject, or put it in the buff"""
        try:
            # If there is no request, get request line
            if self.request is None and constants.CRLF not in self.buff:
                self.buff += util.recv_line(self._socket)

            # If we have the request line, but don't have request object, creat
            # one
            if self.request is None and constants.CRLF in self.buff:
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
                    '%s%s' % (constants.BASE, os.path.normpath(uri)))
                self.file = FileObject.FileObject(
                    file_name, self._buff_size)
                self.request = Request.Request(method, uri)
                self.buff = ""

            # If we do have request line, get headers
            if self.request is not None:
                while True:
                    buf = util.recv_line(self._socket)
                    if constants.CRLF not in buf:
                        break
                    self._recv_buff += buf
                lines = self._recv_buff.split(constants.CRLF)
                for line in lines[:-1]:
                    self.request.add_header(*lines.split(": ", 2))
                if ": " in lines[-1]:
                    self.request.add_header(*lines.split(": ", 2))
                    self._recv_buff = ""
                else:
                    self._recv_buff = lines[-1]

        except IOError as e:
            self.logger.error(traceback.format_exc)
            if e.errno == errno.ENOENT:
                self._send_buff = util.creat_error(404, 'File Not Found', e)
            else:
                self._send_buff = util.creat_error(500, 'Internal Error', e)
        except Exception as e:
            self.logger.error(traceback.format_exc)
            self._send_buff = util.creat_error(500, "Internal Error", e)
            raise e

    def send(self):
        """ Fill self.send_buff with all the data it needs and then send it
        """
        if self.request is not None and self.file is not None:
            if not self.request.sent_status:
                self._send_buff += (
                    "%s 200 OK\r\n"
                    "Content-Length: %s\r\n"
                    "Content-Type: %s\r\n"
                    "\r\n"
                ) % (
                    constants.HTTP_VERSION,
                    self.file.get_file_size(),
                    MIME_MAPPING.get(
                        os.path.splitext(
                            self.request.get_uri
                        )[1].lstrip('.'),
                        'application/octet-stream',
                    ),
                )
                self.request.sent_status = True
            read_all = self.file.check_read_all()
            if self.check_finished_request():
                raise CustomExceptions.FinishedRequest
            free_space_in_buffer = self._buff_size - len(self._send_buff)
            if not read_all and free_space_in_buffer > 0:
                self._send_buff += self.file.read_buff(free_space_in_buffer)
            self._send_my_buff()
            if self.check_finished_request():
                raise CustomExceptions.FinishedRequest

    def check_finished_request(self):
        """Check if we finished the request"""
        return (self.request.sent_status and self.file.check_read_all()
                and not self._send_buff)

    def _send_my_buff(self):
        """Send the data in self._send_buff"""
        while self._send_buff:
            try:
                self._send_buff = self._send_buff[
                    self._socket.send(self._send_buff):]
            except socket.error as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                else:
                    break

    def get_send_buff(self):
        """Return _send_buff"""
        return self._send_buff
