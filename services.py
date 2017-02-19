"""All the services get the method we need and return the data
"""

import time
from . import constants
BASE_HTTP = """<HTML>
    <head>
        <title>%s</title>
    </head>
    <BODY>
        %s
    </BODY>
</HTML>"""


class Service(object):

    NAME = 'base'

    def __init__(self):
        pass

    def content(self):
        pass

    def headers(self):
        pass


class Clock(Service):

    NAME = '/clock'

    def content(self):
        return BASE_HTTP % (
            Clock.__name__,
            """local timezone %s<br>
            UTC timezone %s""" % (
                time.strftime(
                    "%z %H:%M:%S"
                ),
                time.strftime(
                    "%H:%M:%S",
                    time.gmtime()))
        )

    def headers(self):
        return (
            "%s 200 OK\r\n"
            "Content-Length: %s\r\n"
            "Content-Type: %s\r\n"
            "\r\n"
        ) % (
            constants.HTTP_VERSION,
            self.content(),
            'text/html',
        )

class Creat_new_game(Service):
    NAME = '/new'
    
    
    <form action="/register_quiz" method = "get">
    Name of quiz:<br>
    <input type="text" name="quiz-name"><br>
    <input type="submit" value="Start game!"
    </form>
    #WIP