"""All the services get the method we need and return the data
"""

import os.path
import time

from . import constants


# Base for  any HTTP page, you give it the title and the body of the page
BASE_HTTP = """<HTML>
    <head>
    <title>%s</title>
    </head>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
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
            """clock""",
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
        return BASE_HTTP % ("New Game!",
                            """<form action = "/register_quiz" method = "get" >
                               <font size="4">Name of quiz:</font><br>
                               <input type = "text" name = "quiz_name"
                                size="21">
                               <br><br>
                               <input type = "submit" value = "Start game!"
                                style="height:50px; width:150px">
                                </form >"""
                            )


class register_quiz(Service):
    NAME = "/register_quiz"

    def __init__(self, quiz_name):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._quiz_name = quiz_name[0]
        if os.path.isfile(os.path.normpath("PyHoot\Files\%s.xml" %
                                           os.path.normpath(self._quiz_name))):
            self.content = self.right
        else:
            self.content = self.wrong

    def right(self):
        return BASE_HTTP % ("right", "WIP")

    def wrong(self):
        return BASE_HTTP % (
            "No such quiz",
            """<form action = "/register_quiz" method = "get" >
               <font size="4">No such quiz!<br>Name of quiz:</font><br>
               <input type = "text" name = "quiz_name" size="21"> <br><br >
               <input type = "submit" value = "Start game!"
               style="height:50px; width:150px">
               </form >"""
        )


class join_quiz(Service):
    NAME = "/"  # This is the homepage
    # Phone style

    def content(self):
        return BASE_HTTP % (
            """Join game!""",
            """<form action = "/waiting_room" method = "get">
               <font size ="7">Game Pin</font><br>
               <input type="number" name="pid" style="width: 200px;"
                min="100000000" max="999999999">
               <br><br><input type="submit" value="Join!">
           """

        )


class waiting_room(Service):
    NAME = "/waiting_room"  # TODO: Write this


class answer(Service):
    NAME = "/answer"

    def content(self):
        pass  # TODO: write this
