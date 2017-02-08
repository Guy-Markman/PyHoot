import socket

from . import constants


def creat_nonblocking_socket():
    """ Creat nonblocking socket"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(0)
    return s


def creat_error(code, message, extra):
    """Creat the error we will send to the client"""
    message = (
        "%s %s %s\r\n"
        "Content-Length: %s\r\n"
        "\r\n"
        "%s\r\n"
        "%s\r\n" % (
            constants.HTTP_VERSION,
            code,
            message,
            len(message) + len(str(extra)) + 4,
            message,
            extra
        )
    )
    return message
