"""All the services get the method we need and return the data
"""

import time

from . import constants


# Base for  any HTTP page, you give it the title and the body of the page
BASE_HTTP = """<HTML>
    <head>
        <title>%s</title>
    </head>
    <BODY>
        %s
    </BODY>
</HTML>"""


class Service(object):
    """Base class to all services"""
    NAME = 'base'  # The uri path needed to use this services

    def __init__(self):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read

    def content(self):
        """The body of the service"""
        pass

    def close(self):
        pass

    def headers(self):
        """Headers of the service, base if for any HTTP page"""
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

    def read_buff(self, buff_size):
        """return the content page and update self._finished_reading"""
        self.read_pointer += buff_size
        return self.content()[self.read_pointer - buff_size:self.read_pointer]

    def get_status(self):
        """Return self._finished_reading"""
        return self._finished_reading


class Clock(Service):
    """HTTP page of local time and UTC time"""
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
    """Let the manager of the game choose the quiz he wants"""

    def content(self):
        return BASE_HTTP % ("New Game!", """
        <form action = "/register_quiz" method = "get" >
        Name of quiz:
            <br >
        <input type = "text" name = "quiz-name" > <br><br >
        <input type = "submit" value = "Start game!">
        </form >"""
                            )
