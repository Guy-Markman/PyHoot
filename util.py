import os
import socket

HTTP_VERSION = "HTTP/1.1"
MIME_MAPPING = {
    'html': 'text/html',
    'png': 'image/png',
    'txt': 'text/plain',
    'xml': 'text/xml'
}


def creat_nonblocking_socket(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(0)
    return s


# return tupple (code, response)
def creat_http_headers_response(filename):
    if not os.path.isfile(filename):
        response = (
            404,
            """%s 404 File Not Found\r\n
            Content-Type: text/plain\r\n
            \r\n""" % (HTTP_VERSION)
        )
    else:
        response = (
            200,
            """%s 200 OK\r\n
            Content-Length: %s\r\n
            Content-Type: %s\r\n
            \r\n""" % (
                HTTP_VERSION,
                os.path.getsize(filename),
                MIME_MAPPING.get(
                    os.path.splitext(
                        filename
                    )[1].lstrip('.'),
                    'application/octet-stream',
                ),
            ))
    return response
