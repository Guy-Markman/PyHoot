"""All the services get the method we need and return the data
"""

import os.path
import time

from . import util


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
        self._content_page = self.content()

    def content(self):
        """The body of the service"""
        pass

    def close(self):
        pass

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        return util.create_headers_response("200", "OK", len(self.content()),
                                            extra_headers=extra, type=".html")

    def read_buff(self, buff_size):
        """return the content page and update self._finished_reading"""
        self.read_pointer += buff_size
        return self._content_page[self.read_pointer - buff_size:
                                  self.read_pointer]

    def get_status(self):
        """Return self._finished_reading"""
        return self._finished_reading


class Clock(Service):
    """HTTP page of local time and UTC time"""
    NAME = '/clock'

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
                                size="21" autocomplete="off">
                               <br><br>
                               <input type = "submit" value = "Start game!"
                                style="height:50px; width:150px">
                                </form >"""
                            )


class register_quiz(Service):
    NAME = "/register_quiz"

    def __init__(self, quiz_name, quiz_pid):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._quiz_name = quiz_name[0]
        self._quiz_pid = quiz_pid
        if os.path.isfile(os.path.normpath("PyHoot\Files\%s.xml" %
                                           os.path.normpath(self._quiz_name))):
            self.content = self.right
            self.right_page = True
        else:
            self.content = self.wrong
            self.right_page = False
        self._content_page = self.content()

    def right(self):
        return BASE_HTTP % ("Join!",
                            """<font size = 7>Now you can join the Game!<br>
        Pid %d</font>""" % self._quiz_pid)

    def wrong(self):
        return BASE_HTTP % (
            "No such quiz",
            """<form action = "/register_quiz" method = "get" >
               <font size="4">No such quiz!<br>Name of quiz:</font><br>
               <input type = "text" name = "quiz_name" size="21"
               autocomplete="off"> <br><br >
               <input type = "submit" value = "Start game!"
               style="height:50px; width:150px">
               </form >"""
        )

    def get_quiz(self):
        return self._quiz_name


class join_quiz(Service):
    NAME = "/"  # This is the homepage

    def content(self):
        return BASE_HTTP % (
            """Join game!""",
            """<form action = "/choose_name" method = "get">
               <font size ="7">Game Pin</font><br>
               <input type="number" name="pid" style="width: 200px;"
                min="100000000" max="999999999" autocomplete="off">
               <br><br><input type="submit" value="Join!" style="height:50px;
                width:150px">
           """
        )


class choose_name(Service):
    NAME = "/choose_name"

    def __init__(self, common, pid):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        print common.pid_client.get(int(pid[0]))
        if common.pid_client.get(int(pid[0])) is not None:
            self.content = self.right
            self.right_page = True
        else:
            self.content = self.wrong
            self.right_page = False
        self._content_page = self.content()

    def right(self):
        return BASE_HTTP % (
            "Choose name",
            """<form action = "/waiting_room_start" method = "get">
               <font size = "6"> Choose name</font></br>
               <input type="text" name="name" style="width: 200px;">
               <br><br><input type="submit" value="Start Playing!"
                style="height:50px;width:150px">
           """
        )

    def wrong(self):
        return BASE_HTTP % (
            """Join game!""",
            """<form action = "/choose_name" method = "get">
               <font size ="7">No such Game Pin, enter right one</font><br>
               <input type="number" name="pid" style="width: 200px;"
                min="100000000" max="999999999" autocomplete="off">
               <br><br><input type="submit" value="Join!" style="height:50px;
                width:150px">
           """
        )


class waiting_room_start(Service):
    NAME = "/waiting_room_start"  # TODO: Write this

    def __init__(self, name, common, server_pid):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read

    def get_pid(self):
        return self._pid

    def right():
        return BASE_HTTP % (
            "Please wait",
            """ < font size="6" > Please wait < /font >"""
        )

    def wrong():
        return BASE_HTTP % (
            "Choose name",
            """<form action = "/waiting_room_start" method = "get">
               <font size = "6"> Name taken, Choose name</font></br>
               <input type="text" name="name" style="width: 200px;">
               <br><br><input type="submit" value="Start Playing!"
                style="height:50px;width:150px">
           """
        )


class answer(Service):
    NAME = "/answer"

    def content(self):
        return BASE_HTTP % (
            "Play!",
            """ < form action="/wait_answer" style="float:left;" method="GET" >
                < input type="hidden" name="answer" value="A" >
                <input type="submit" value="A" style="height: 150px;
                 width: 150px; font - size: 50px; "/ >
            < /form >
            <form action="/wait_answer" method="GET" >
                < input type="hidden" name="answer" value="B" >
                <input type="submit" value="B" style="height: 150px;
                 width: 150px; font - size: 50px; "/ >
            < /form >
            <form action="/wait_answer" style="float:left;" method="GET" >
                < input type="hidden" name="answer" value="C" >
                <input type="submit" value="C" style="height: 150px;
                 width: 150px; font - size: 50px; "/ >
            < /form >
            <form action="/wait_answer" method="GET" >
                < input type="hidden" name="answer" value="D" >
                <input type="submit" value="D" style="height: 150px;
                 width: 150px; font - size: 50px; "/ >
            < /form > """
        )


class wait_answer(Service):
    NAME = "/wait_answer"

    def __init__(self, answer):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self.answer = answer
        self._content_page = self.content()

    def content(self):
        return BASE_HTTP % (
            "Please wait",
            """ < font size="6" > Please wait < /font >"""
        )
