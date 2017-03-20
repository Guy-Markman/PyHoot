"""All the services get the method we need and return the data
"""

import os.path
import time

from . import constants, util


class Service(object):
    """Base class to all services"""
    NAME = 'base'  # The uri path needed to use this services

    def __init__(self):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._content_page = self.content()

    def content(self):
        """The body of the service"""
        return ""

    def close(self):
        pass

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        return util.create_headers_response(200,
                                            len(self._content_page),
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
        return constants.BASE_HTML % (
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
        return constants.BASE_HTML % ("New Game!",
                                      """<center>
                               <form action="/register_quiz" method = "get">
                               <font size="5">Name of quiz:</font><br>
                               <input type="text" name="quiz_name"
                                size="21" autocomplete="off">
                               <br><br>
                               <input type="submit" value="Start game!"
                                style="height:50px; width:150px">
                                </form>
                                </center>"""
                                      )


class register_quiz(Service):
    NAME = "/register_quiz"

    def __init__(self, quiz_name, pid):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._quiz_name = quiz_name[0]
        self._pid = pid
        if os.path.isfile(os.path.normpath("PyHoot\Quizes\%s.xml" %
                                           os.path.normpath(self._quiz_name))):
            self.content = self.right
            self.right_page = True
        else:
            self.content = self.wrong
            self.right_page = False
        self._content_page = self.content()

    def right(self):
        return constants.BASE_HTML % ("Join!",
                                      """
                    <center>
                    <font size = 7>Now you can join the Game!<br>
                    Pid %d</font><br><br>
                    Connected players
                    <p id="names">
                    </p>
                    <br><br>
                    <input type="button" value="Start playing"
                    onclick="window.location = '/opening'">
                    <script>
                    window.setInterval(function(){
                      getnames();
                    }, 1000);
                    function getnames() {
                         var xhttp = new XMLHttpRequest();
                         xhttp.onreadystatechange = function() {
                             if (this.readyState == 4 && this.status == 200){
                                 document.getElementById("names").innerHTML =
                                 this.responseText;
                             }
                         };
                         xhttp.open("GET", "getnames", true);
                         xhttp.send();
                    }
                    </script>
                    </center>
                    """ % self._pid)

    @staticmethod
    def wrong():
        return constants.BASE_HTML % (
            "No such quiz",
            """<center>
               <form action="/register_quiz" method="get">
               <font size="4">No such quiz!<br>Name of quiz:</font><br>
               <input type = "text" name = "quiz_name" size="21"
               autocomplete="off"> <br><br>
               <input type="submit" value="Start game!"
               style="height:50px; width:150px">
               </form >
               </center>"""
        )

    def get_quiz(self):
        return self._quiz_name


class join_quiz(Service):
    NAME = "/"  # This is the homepage

    def content(self):
        return constants.BASE_HTML % (
            """Join game!""",
            """<center>
               <form action="/choose_name" method="get">
               <font size ="7">Game Pin</font><br>
               <input type="number" name="pid" style="width: 200px;"
                min="%s" max="%s" autocomplete="off">
               <br><br><input type="submit" value="Join!" style="height:50px;
                width:150px">
               </center>
           """ % (constants.MIN_PID, constants.MAX_PID)
        )


class choose_name(Service):
    NAME = "/choose_name"

    def __init__(self, common, pid):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        if common.pid_client.get(int(pid)) is not None:
            self.content = self.right
            self.right_page = True
        else:
            self.content = self.wrong
            self.right_page = False
        self._content_page = self.content()

    @staticmethod
    def right():
        return constants.BASE_HTML % (
            "Choose name",
            """<center>
               <form action = "/waiting_room_start" method = "get">
               <font size = "6"> Choose name</font></br>
               <input type="text" name="name"  pattern=".{3,}"
                required title="3 characters minimum" style="width: 200px;">
               <br><br><input type="submit" value="Start Playing!"
                style="height:50px;width:150px">
                </center>
           """
        )

    @staticmethod
    def wrong():
        return constants.BASE_HTML % (
            """Join game!""",
            """<center>
               <form action="/choose_name" method="get">
               <font size ="7">No such Game Pin, enter right one</font><br>
               <input type="number" name="pid" style="width: 200px;"
                min="100000000" max="999999999" autocomplete="off">
               <br><br><input type="submit" value="Join!" style="height:50px;
                width:150px">
                </center>
           """
        )


class waiting_room_start(Service):
    NAME = "/waiting_room_start"  # TODO: Write this

    def __init__(self, name, common, server_pid):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        if name[0] not in common.pid_client[server_pid].get_player_dict():
            self.content = self.right
            self.right_page = True
        else:
            self.content = self.wrong
            self.right_page = False
        self._content_page = self.content()

    def get_pid(self):
        return self._pid

    @staticmethod
    def right():
        return constants.BASE_HTML % (
            "Please wait",
            """<center>
               <font size="6">Please wait</font>
               <br><br>
               <input type="button" value="Disconnect" onclick=
               "disconnect_function();"/>
               </center>
               <script>
               function disconnect_function(){
                    var xhttp = new XMLHttpRequest();
                    xhttp.onreadystatechange = function() {
                        if (this.readyState == 4 && this.status == 200){
                            window.location.href = '/';
                        }
                    };
                    xhttp.open("GET", "diconnect_user", true);
                    xhttp.send();
               }
               </script>
               """
        )

    @staticmethod
    def wrong():
        return constants.BASE_HTML % (
            "Choose name",
            """<center>
               <form action="/waiting_room_start" method="get">
               <font size="6"> Name taken, Choose name</font></br>
               <input type="text" name="name" style="width: 200px;">
               <br><br><input type="submit" value="Start Playing!"
                style="height:50px;width:150px">
                </center>
           """
        )


class answer(Service):
    NAME = "/answer"

    def content(self):
        return constants.BASE_HTML % (
            "Play!",
            """ <form action="/wait_answer" style="float:left;" method="GET">
                <input type="hidden" name="answer" value="A">
                <input type="submit" value="A" style="height: 150px;
                 width: 150px; font-size: 50px;"/>
            </form>
            <form action="/wait_answer" method="GET">
                <input type="hidden" name="answer" value="B">
                <input type="submit" value="B" style="height: 150px;
                 width: 150px; font-size: 50px;"/>
            </form>
            <form action="/wait_answer" style="float:left;" method="GET">
                <input type="hidden" name="answer" value="C">
                <input type="submit" value="C" style="height: 150px;
                 width: 150px; font-size: 50px;"/>
            </form>
            <form action="/wait_answer" method="GET">
                <input type="hidden" name="answer" value="D">
                <input type="submit" value="D" style="height: 150px;
                 width: 150px; font-size: 50px;"/>
            </form>"""
        )


class wait_answer(Service):
    NAME = "/wait_answer"

    def __init__(self, game, answer):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        game.add_answer(answer)
        self._content_page = self.content()

    def content(self):
        return constants.BASE_HTML % (
            "Please wait",
            """<center><font size="6">Please wait</font></center>"""
        )


class test_xmlhttprequest(Service):
    NAME = "/test_xmlhttprequest"

    def content(self):
        return constants.BASE_HTML % (
            "test",
            """<p id="test">
               <button type="button" onclick="bip()">BIP</button>
               </p>
               <script>
               function bip() {
                    var xhttp = new XMLHttpRequest();
                    xhttp.onreadystatechange = function() {
                        if (this.readyState == 4 && this.status == 200){
                            document.getElementById("test").innerHTML =
                            this.responseText;
                        }
                    };
                    xhttp.open("GET", "bop.txt", true);
                    xhttp.send();
               }
               </script>
               """
        )


class getnames(Service):
    NAME = "/getnames"

    def __init__(self, game, common):
        self._game = game
        self._common = common
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._content_page = self.content()

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        return util.create_headers_response(200,
                                            len(self._content_page),
                                            extra_headers=extra, type=".txt")

    def content(self):
        names = []
        for player in self._game.get_player_dict().values:
            name = player.name
            if  name is not None:
                names.append(name)
        return "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join(names)


class diconnect_user(Service):
    NAME = "/diconnect_user"

    def __init__(self, pid, common, game):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._content_page = self.content()

        self._pid = pid

        common.pid_client.pop(pid, None)
        try:
            if game.NAME == "MASTER":
                for pid_player in game.get_player_dict().keys():
                    player = common.get(pid_player)
                    if player is not None:
                        player.game_master = None
            if game.NAME == "PLAYER":
                game.game_master.remove_player(pid)
        except AttributeError:
            pass


class opening(Service):
    NAME = "/opening"

    def __init__(self, game):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._content_page = game.get_parser().get_html_start()


class question(Service):
    NAME = "/question"

    def __init__(self, game):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        parser = game.get_parser()
        if parser.get_left_questions() > 0:
            parser.moved_to_next_page()
            self._content_page = parser.get_html_question()
        else:
            self._content_page = """<html>
            <body onload="window.location.href="/finish">
            </body>
</html>
            """


class leaderboard(Service):
    NAME = "/leaderboard"
    
    def __init__(self, game):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._content_page = game.get_html_leaderboard())

class finish(Services):
    NAME = "/finish"
    
    def __init__(self, game):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._game = game
    
    def content(self)
        return "WIP"