"""Constants for the program"""
## @file constants.py Constants for the program

## Base for  any HTTP page, you give it the title and the body of the page
BASE_HTML = """<HTML>
    <head>
    <title>%s</title>
    </head>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <BODY>
        %s
    </BODY>
</HTML>"""

## The buff size for each time
BUFF_SIZE = 1024


## States for server
## CLOSE - We are closing this socket
CLOSE = 0

## SERVER - This socket is a server
SERVER = 1

## CLIENT - This socket is a client
CLIENT = 2

## New line
CRLF = "\r\n"


## Double new line
DOUBLE_CRLF = 2 * CRLF

## Encoding for files
ENCODING = 'utf-8'

## HTTP Version we are using
HTTP_VERSION = "HTTP/1.1"

## How many characters in cookie
LENGTH_COOKIE = 16

## Longest header possible
MAX_HEADER_LENGTH = 4096

## Biggest joinnumber
MAX_PID = 999999

## Smallest join number
MIN_PID = 100000


## Types of games
## NONE - Not playing
NONE = 0

## MASTER - game MASTER
MASTER = 1

## PLAYER - player
PLAYER = 2


## Longest Question time
QUESTION_TIME = 3000
