import os
import socket

MAX_BLOCK_SIZE = 1024
MAX_HEADER_LENGTH = 4096
CRLF = "\r\n"
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


def recv_line(
    s,
    buf,
    max_length=MAX_HEADER_LENGTH,
    block_size=MAX_BLOCK_SIZE,
):
    while True:
        if len(buf) > max_length:
            raise RuntimeError(
                'Exceeded maximum line length %s' % max_length)
        n = buf.find(CRLF)
        if n != -1:
            break
        t = s.recv(block_size)
        if not t:
            raise RuntimeError('Disconnect')
        buf += t
    return buf[:n].decode('utf-8'), buf[n + len(CRLF):]
