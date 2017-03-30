"""All the services get the method we need and return the data
"""

import os.path
import time

from . import base, constants, game, util


class Service(base.Base):
    """Base class to all services"""
    NAME = 'base'  # The uri path needed to use this services

    def __init__(self):
        self.finished_reading = False  # Did we read everything from read?
        self.read_pointer = 0  # How much did we read from read
        self._content_page = None

    def content(self):
        """The body of the service"""
        return ""

    def close(self):
        pass

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        if self._content_page is None:
            self._content_page = self.content()
        return util.create_headers_response(200,
                                            len(self._content_page),
                                            extra_headers=extra, type=".html")

    def read_buff(self, buff_size):
        """return the content page and update self._finished_reading"""
        if self._content_page is None:
            self._content_page = self.content()
        self.read_pointer += buff_size
        return self._content_page[self.read_pointer - buff_size:
                                  self.read_pointer]

    def get_status(self):
        """Return self._finished_reading"""
        return self._finished_reading


class TXTService(Service):

    def __init__(self):
        super(TXTService, self).__init__()

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        if self._content_page is None:
            self._content_page = self.content()
        return util.create_headers_response(200,
                                            len(self._content_page),
                                            extra_headers=extra, type=".html")


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


class register_quiz(Service):
    NAME = "/register_quiz"

    def __init__(self, quiz_name, common, pid=None):
        super(register_quiz, self).__init__()
        self._quiz_name = quiz_name[0]
        if pid is not None:
            util.remove_from_sysyem(common, pid)
        g = self.register_master(quiz_name[0], common)
        self.master_pid = g.pid

    def headers(self, extra):
        extra.update({"Location": "/quiz.html",
                      "Set-Cookie": "pid=%s" % self.master_pid})
        return util.create_headers_response(302, extra_headers=extra)

    def register_master(self, quiz_name, common):
        m = game.GameMaster(quiz_name, common)
        common.pid_client[m.pid] = m
        return m


class homepage(Service):
    NAME = "/"  # This is the homepage

    def headers(self, extra):
        extra.update({"Location": "/home.html"})
        return util.create_headers_response(302, extra_headers=extra)


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
        super(wait_answer, self).__init__()
        game.add_answer(answer)

    def content(self):
        return constants.BASE_HTML % (
            "Please wait",
            """<center><font size="6">Please wait</font></center>"""
        )


class getnames(TXTService):
    NAME = "/getnames"

    def __init__(self, game, common):
        super(getnames, self).__init__()
        self._game = game
        self._common = common

    def content(self):
        names = []
        for player in self._game.get_player_dict().values():
            name = player.name
            if name is not None:
                names.append(name)
        return "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join(names)


class diconnect_user(Service):
    NAME = "/diconnect_user"

    def __init__(self, pid, common, game):
        super(diconnect_user, self).__init__()

        common.pid_client.pop(pid, None)
        try:
            if game.TYPE == "MASTER":
                for pid_player in game.get_player_dict().keys():
                    player = common.get(pid_player)
                    if player is not None:
                        player.game_master = None
                self.logger.debug("Disconneted master")
            if game.TYPE == "PLAYER":
                game.game_master.remove_player(int(pid))
                self.logger.debug("Disconnect player")
        except AttributeError:
            pass


class opening(Service):
    NAME = "/opening"

    def __init__(self, game):
        super(opening, self).__init__()
        self._content_page = game.get_parser().get_html_start()


class question(Service):
    NAME = "/question"

    def __init__(self, game):
        super(question, self).__init__()
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


class check_test(TXTService):
    NAME = "/check_test"

    def __init__(self, pid, common):
        super(check_test, self).__init__()
        self.data = int(pid[0])
        self.common = common

    def content(self):
        return str((
            self.data in self.common.pid_client and
            self.common.pid_client[self.data].TYPE == "MASTER"
        ))


class check_name(TXTService):
    NAME = "/check_name"

    def __init__(self, pid, name, common):
        super(check_name, self).__init__()
        self.data = int(pid[0])
        self.name = name[0]
        self.common = common

    def content(self):
        ans = "False"
        if self.data in self.common.pid_client:
            master = self.common.pid_client[self.data]
            if master.TYPE == "MASTER":
                name_list = []
                for player in master.get_player_dict().values():
                    name_list.append(player.name)
                if self.name not in name_list:
                    ans = "True"
        return ans


class join(Service):
    NAME = "/join"

    def __init__(self, pid, name, common):
        super(join, self).__init__()
        pid = pid[0]
        util.remove_from_sysyem(common, pid)
        g = self.register_player(pid, name[0], common)
        self.player_pid = g.pid

    def headers(self, extra):
        extra.update({"Location": "/game.html",
                      "Set-Cookie": "pid=%s" % self.player_pid})
        return util.create_headers_response(302, extra_headers=extra)

    def register_player(self, pid, name, common):
        g = game.GamePlayer(common.pid_client[int(pid)], common, name)
        common.pid_client[g.pid] = g
        g.game_master.add_player(g.pid, g)
        return g


class check_test_exist(TXTService):
    NAME = "/check_test_exist"

    def __init__(self, quiz_name):
        super(check_test_exist, self).__init__()
        self._quiz_name = quiz_name[0]

    def content(self):
        print self._quiz_name
        return str(
            os.path.isfile(
                os.path.normpath("PyHoot\Quizes\%s.xml" %
                                 os.path.normpath(self._quiz_name)
                                 )
            )
        )


class new(Service):
    NAME = "/new"  # This is the homepage

    def headers(self, extra):
        extra.update({"Location": "/new.html"})
        return util.create_headers_response(302, extra_headers=extra)
