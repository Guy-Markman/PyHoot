"""Constants for the program"""
BASE = '.'
# Base for  any HTTP page, you give it the title and the body of the page
BASE_HTML = """<HTML>
    <head>
    <title>%s</title>
    </head>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <BODY>
        %s
    </BODY>
</HTML>"""
BUFF_SIZE = 1024
CLOSE, SERVER, CLIENT = range(3)
CRLF = "\r\n"
DOUBLE_CRLF = 2 * CRLF
ENCODING = 'utf-8'
HTTP_VERSION = "HTTP/1.1"
LENGTH_COOKIE = 16
MAX_HEADER_LENGTH = 4096
MAX_PID = 999999
MIN_PID = 100000
NONE, MASTER, PLAYER = range(3)
QUESTION_TIME = 3000
