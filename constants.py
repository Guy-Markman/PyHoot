"""Constants for the program"""
BASE = '.'
BUFF_SIZE = 1024
CLOSE, SERVER, CLIENT = range(3)
CRLF = "\r\n"
DOUBLE_CRLF = 2 * CRLF
ENCODING = 'utf-8'
HTTP_VERSION = "HTTP/1.1"
MAX_HEADER_LENGTH = 4096
MIME_MAPPING = {
    '.html': 'text/html',
    '.png': 'image/png',
    '.txt': 'text/plain',
    '.py': 'application/octet-stream'
}
NONE, MASTER, PLAYER = range(3)
