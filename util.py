import mimetypes
import socket

from . import constants


def creat_nonblocking_socket():
    """ Creat nonblocking socket"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(0)
    return s


def create_headers_response(
    code,
    message,
    length,
    extra_headers=None,
    type=None
):
    """create the headers part of the request
        Args:
            code - The HTTP code for the request
            message - The HTTP code message for the request
            length - length of the message
            extra_headers - a list of lists where every list is the header name
                            and then header content.
                            example: [["header name", "header content"]]
            type - The type of the file (is we send a file).
                   example: ".py"
    """
    message = ("%s %s %s\r\n"
               "Content-Length: %s\r\n" % (constants.HTTP_VERSION,
                                           code, message, length)
               )
    if type is not None:
        mimetypes.init()
        message += "Content-Type: %s\r\n" % (
            mimetypes.types_map[type] if type in mimetypes.types_map and type != ".py"
            else
            'application/octet-stream')
    if extra_headers is not None:
        for extra in extra_headers:
            message += "%s: %s\r\n" % (extra, extra_headers[extra])
    message += "\r\n"
    return message


def creat_error(code, message, extra):
    """Creat the error we will send to the client"""
    message = (
        "%s"
        "%s\r\n"
        "%s\r\n" % (
            create_headers_response(
                code,
                message,
                len(message) + len(str(extra)) + 4,
            ),
            message,
            extra
        )
    )
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
