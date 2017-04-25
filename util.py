
import httplib
import mimetypes
import socket
from xml.etree import ElementTree

from . import constants


def creat_nonblocking_socket():
    """ Creat nonblocking socket"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(0)
    return s


def create_headers_response(
    code,
    length=None,
    extra_headers=None,
    type=None,
):
    """create the headers part of the request
        Args:
            code - The HTTP code for the request
            length - length of the message
            extra_headers - a list of lists where every list is the header name
                            and then header content.
                            example: [["header name", "header content"]]
            type - The type of the file (is we send a file).
                   example: ".py"
    """
    message = ("%s %s %s%s" % (
        constants.HTTP_VERSION,
        code,
        httplib.responses[code],
        constants.CRLF,
    )
    )
    if length is not None:
        message += "Content-Length: %s%s" % (length, constants.CRLF)
    if type is not None:
        mimetypes.init()
        if type in mimetypes.types_map and type != ".py":
            content_type = mimetypes.types_map[type]
        else:
            content_type = 'application/octet-stream'
        message += "Content-Type: %s%s" % (content_type, constants.CRLF)
    if extra_headers is not None:
        for extra in extra_headers:
            message += "%s: %s%s" % (extra,
                                     extra_headers[extra], constants.CRLF)
    message += constants.CRLF
    return message


def creat_error(code, extra):
    """Creat the error we will send to the client
    Arguemesnt:
    code: HTTP status code
    extra: any thing you want to put after the status message
    """
    http_message = httplib.responses[code]
    message = (
        "%s"
        "%s\r\n"
        "%s\r\n" % (
            create_headers_response(
                code,
                len(http_message) + len(str(extra)) + 4,
            ),
            http_message,
            extra
        )
    )

    return message


def remove_from_sysyem(common, pid):
    g = common.pid_client.pop(pid, None)
    if g is not None:
        if g.TYPE == "MASTER":
            common.join_number.pop(g.join_number)
            for player in common.pid_client.values():
                player.game_master = None
        if g.TYPE == "PLAYER":
            if g.game_master is not None:
                g.game_master.remove_player(pid)


def to_string(element):
    return ElementTree.tostring(element, constants.ENCODING)


def boolean_to_xml(boolean):
    return to_string(ElementTree.Element("Root", {"answer": str(boolean)}))
