import socket

MAX_BLOCK_SIZE = 1024
MAX_HEADER_LENGTH = 4096
CRLF = "\r\n"


def creat_nonblocking_socket(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(0)
    return s


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
