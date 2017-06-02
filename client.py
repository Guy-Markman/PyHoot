## @package PyHoot.client
# The client of the server
## @file client.py Implementation of @ref PyHoot.client


import Cookie
import errno
import os.path
import socket
import urlparse

from . import (base, constants, custom_exceptions, file_object, request,
               services, util)

### Methods supported for the server
SUPPORTED_METHODS = ('GET')

## States for the server
## Havn't got status yet
INITIALIZED = 0

## Got status, sending own status
SENDING_STATUS = 1

## Sent status, sending data
SENDING_DATA = 2

## Finished request and response
FINISHED = 3

## Error in client
ERROR = 4


## Services availible
SERVICES_LIST = {service.NAME: service for service in
                 (services.Service.__subclasses__() +
                  services.XMLService.__subclasses__()
                  )}


class Client(base.Base):
    """The client of the server handles everything by itself
        Arguments:
                self.socket = The socket of the client.
                self.common = The common library for the client
                self._recv_buff = Any data it has recieved but hasn't procssed
                                  yet.
                self._send_buff = All the data that needs to be sent but
                                  hasn't been sent yet.
                self._buff_size = The buff size of the server.
                self._file = FileObject or service object of the file\service
                             the request wants.
                self._request = The request object of the request we got
                self._base_directory = The base directory which we will use for
                                       the file locations.
    """

    def __init__(
        self,
        s,
        buff_size,
        base_directory,
        common
    ):
        """The client of the server handles everything by itself
           Arguements:
               s: the socket of this client, CANNOT BE MODIFIED.
               buff_size: The buff size of the server.
               base_directory: The base directory which we will use for the
                               file locations.
        """
        super(Client, self).__init__()

        ## The socket of this client, CANNOT BE MODIFIED
        self.socket = s
        self._buff_size = buff_size
        self._base_directory = base_directory

        ## The common library for the client
        self.common = common

        self._file = None
        self._game = None
        self._send_buff = ""
        self._recv_buff = ""
        self._request = None
        self._state = INITIALIZED
        self._game_state = constants.NONE
        self._extra_headers = {}

    def get_socket(self):
        """Get the socket of this client."""
        return self.socket

    def _test_http_and_creat_objects(self):
        parsed_lines = self._recv_buff.split(constants.CRLF, 1)
        req = parsed_lines[0].split(' ', 2)
        if req[2] != constants.HTTP_VERSION:
            raise RuntimeError('Not HTTP protocol')
        if len(req) != 3:
            raise RuntimeError('Incomplete HTTP protocol')
        self.logger.debug("Req, %s", req)
        method, uri, signature = req
        if method not in SUPPORTED_METHODS:
            raise RuntimeError("HTTP unspported method '%s'" % method)
        if not uri or uri[0] != '/' or '\\' in uri:
            raise RuntimeError("Invalid URI")
        if len(parsed_lines) == 1:
            self._recv_buff = ""
        else:
            self._recv_buff = parsed_lines[1]
        self._request = request.Request(method, uri)
        self._get_headers()
        self._set_game()
        uri_path = urlparse.urlparse(uri).path
        if uri_path not in SERVICES_LIST.keys():
            file_type = os.path.splitext(uri_path)[1]
            self._file = file_object.FileObject(uri_path, self._base_directory)
        else:
            # The service initiatiator
            service_function = SERVICES_LIST[uri_path]

            # dictionary of the query of uri
            dic_argument = urlparse.parse_qs(
                urlparse.urlparse(uri).query)
            dic_argument.update({"common": self.common,
                                 "base_directory": self._base_directory})
            if self._game is not None:
                dic_argument.update({"pid": self._game.pid, "game":
                                     self._game})
                if (self._game.TYPE == "PLAYER" and
                        self._game.game_master is not None):
                    dic_argument.update(
                        {"server_pid": self._game.game_master.pid})
            # Remove un-usable keys
            dic_argument.pop('self', None)
            self.logger.debug("dic arguement %s", dic_argument)
            # Creat a tupple of the arguments for service_function that
            # are in dic_argument
            self._file = service_function(
                *(dic_argument[arg] for arg in
                  service_function.__init__.__code__.co_varnames if
                  arg in dic_argument)
            )
        if self._file.NAME == "FILE":
            self._send_buff += (
                util.create_headers_response(200,
                                             self._file.get_file_size(),
                                             self._extra_headers,
                                             file_type)
            )
        else:
            self._send_buff += self._file.headers(self._extra_headers)
        self.logger.debug(
            "Created file\service and request and might setted game")
        self._state = SENDING_STATUS

    def _get_headers(self):
        """Getting and setting the headers"""
        self.logger.debug("Start _get_headers")
        if constants.CRLF in self._recv_buff:
            self.logger.debug("Inside crlf")
            dic_headers = {}
            for line in self._recv_buff.splitlines():
                if line != "":
                    split_line = line.split(":")
                    dic_headers[split_line[0].lower()] = split_line[
                        1].lstrip(' ')
            self.logger.debug("dic_headers %s", dic_headers)
            if "cookie" in dic_headers:
                self._request.add_header("cookie", dic_headers["cookie"])
                self.logger.debug("Added cookie, %s", dic_headers["cookie"])
        self._recv_buff = ""

    def _change_to_error(self, error_messege):
        """Changeing the status to error"""
        self._send_buff = error_messege
        self._state = ERROR
        self._recv_buff = ""

    def _set_game_object(self):
        """Setting the game object to self._game using the cookies"""
        cookie = Cookie.BaseCookie(self._request.get_all_header()["cookie"])
        if "pid" in cookie:
            pid = cookie["pid"].value
            if pid in self.common.pid_client:
                self._game = self.common.pid_client[pid]
                self.logger.debug("Set game as %s", self._game)
        else:
            self.logger.debug("Game object not found")

    def _set_game(self):
        """Setting the game. Creating new game object if needed and deleting
        unneeded"""
        headers = self._request.get_all_header()
        if "cookie" in headers:  # Setting game object
            self._set_game_object()

    def recv(self):
        """Recv data from the client socket and process it to Reqeust and
           FileObject, or put it in the buff"""
        try:
            # If there is no request line, get it
            if self._state == INITIALIZED:
                self._recv_data()
                self.logger.debug("after recv %s", self._recv_buff)
            # If we have the request line, but don't have request object, creat
            # one
            if (
                self._state == INITIALIZED and
                constants.CRLF in self._recv_buff
            ):
                self._test_http_and_creat_objects()

            # If we do have request line, get headers
            self.logger.debug("state %s", self._state)
            self.logger.debug("Now recv_buff is %s", self._recv_buff)

        except OSError as e:
            self.logger.error('Exception ', exc_info=True)
            if e.errno == errno.ENOENT:
                self._change_to_error(
                    util.creat_error(
                        404, e))
            else:
                self._change_to_error(
                    util.creat_error(
                        500, e))
        except custom_exceptions.CorruptXML as e:
            self._logger.error("Exception", exc_info=True)
            self._change_to_error(util.creat_error(400, e))
        except Exception as e:
            self.logger.error('Exception ', exc_info=True)
            self._change_to_error(util.creat_error(500, e))

    def send(self):
        """ Fill self.send_buff with all the data it needs and then send it
        """

        if self._state == ERROR:
            self._send_my_buff()
            if self._send_buff == "":
                self._state = FINISHED
        if self._state == SENDING_STATUS:
            if self._send_buff:
                self._send_my_buff()
            else:
                self._state = SENDING_DATA
        if self._state == SENDING_DATA:
            if self._send_buff == "" and self._file is not None:
                r = self._file.read_buff(self._buff_size)
                self._send_buff += r
                if len(r) < self._buff_size:
                    self._file.finished_reading = True
            if self._send_buff != "":
                self._send_my_buff()
            if self._file is not None and self._file.finished_reading:
                self._state = FINISHED

    def check_finished_request(self):
        """Check if we finished the request"""
        return self._state == FINISHED

    def _send_my_buff(self):
        """Send the data in self._send_buff"""
        self.logger.debug("start sending my buff, send_buff %s",
                          self._send_buff)
        try:
            while self._send_buff:
                self._send_buff = self._send_buff[
                    self.socket.send(self._send_buff):]
                self.logger.debug("client sent")
        except Exception as e:
            if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                if e.errno in (
                    errno.WSABASEERR,
                    errno.WSAECONNABORTED,
                    errno.WSAECONNRESET
                ):
                    raise custom_exceptions.Disconnect()
                raise

        self.logger.debug("Sent all that I could, send_buff %s",
                          self._send_buff)

    def get_send_buff(self):
        """Return _send_buff"""
        return self._send_buff

    def _recv_data(
        self,
        max_length=constants.MAX_HEADER_LENGTH,
        block_size=constants.BUFF_SIZE,
    ):
        """Recive data from socket s, if unable return how much it did read"""
        try:
            self.logger.debug("_recv_data %s", self._recv_buff)
            while True:
                n = self._recv_buff.find(constants.CRLF)
                if n != -1:
                    break
                t = self.socket.recv(block_size)
                if not t:
                    raise custom_exceptions.Disconnect()
                self._recv_buff += t
        except socket.error as e:
            if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                if e.errno == errno.WSABASEERR:
                    raise custom_exceptions.Disconnect()
                raise

    def can_recv(self):
        """Decide if it can recive more data or not"""
        ans = len(self._recv_buff) < self._buff_size
        if self._request is not None:
            ans = ans and not self._request.full_request
        return ans

    def can_send(self):
        """Check if the user can send more data"""
        return (
            len(self._send_buff) > 0 or
            self._state in (SENDING_DATA, SENDING_STATUS)
        )

    def get_file(self):
        """Return self._file"""
        return self._file
