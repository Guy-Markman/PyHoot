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
        self.sent_all = False

    def content(self):
        pass

    def headers(self):
        return (
            "%s 200 OK\r\n"
            "Content-Length: %s\r\n"
            "Content-Type: %s\r\n"
            "\r\n"
        ) % (
            constants.HTTP_VERSION,
            len(self.content()),
            'text/html',
        )

    def read(self):
        self.sent_all = True
        return self.content()

    def get_status(self):
        return self.sent_all


class Clock(Service):

    NAME = '/clock'

    def __init__(self):
        super(Clock, self).__init__()

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


class Creat_new_game(Service):
    NAME = '/new'

    def content(self):
        return BASE_HTTP % ("New Game!", """
        <form action = "/register_quiz" method = "get" >
        Name of quiz:
            <br >
        <input type = "text" name = "quiz-name" > <br><br >
        <input type = "submit" value = "Start game!"
        </form >"""
                            )
