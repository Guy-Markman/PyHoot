BASE = '.'
BUFF_SIZE = 1024
CRLF = "\r\n"
HTTP_VERSION = "HTTP/1.1"
MAX_HEADER_LENGTH = 4096
DOUBLE_CRLF = 2 * CRLF
CLOSE, SERVER, CLIENT = range(3)
NONE, MASTER, PLAYER = range(3)
MIME_MAPPING = {
    '.html': 'text/html',
    '.png': 'image/png',
    '.txt': 'text/plain',
    '.py': 'application/octet-stream'
}
