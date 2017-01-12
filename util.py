import errno
import socket

import constants
import CustomExceptions

MAX_HEADER_LENGTH = 4096


def creat_nonblocking_socket():
    """ Creat nonblocking socket"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(0)
    return s


def recv_lines(
    s,
    buf,
    max_length=MAX_HEADER_LENGTH,
    block_size=constants.BUFF_SIZE,
):
    """Recive lines from socket s, if unable return how much it did read"""
    try:
        while True:
            n = buf.find(constants.CRLF)
            if n != -1:
                break
            t = s.recv(block_size)
            if not t:
                raise CustomExceptions.Disconnect
            buf += t
    except socket.error as e:
        if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
            raise
    return buf


def creat_error(code, message, extra):
    """Creat the error we will send to the client"""
    message = (
        "%s %s %s\r\n"
        "Content-Length: %s\r\n\r\n"
        "%s\r\n"
        "%s \r\n" % (
            constants.HTTP_VERSION,
            code,
            message,
            code,
            message,
            extra
        )
    )
    return message
