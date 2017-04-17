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
        return self.finished_reading


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

    def content(self):
        return "done"


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
            util.remove_from_sysyem(
                common,
                pid,
            )
        g = self.register_master(quiz_name[0], common)
        self.master_pid = g.pid

    def headers(self, extra):
        extra.update({"Location": "/quiz.html",
                      "Set-Cookie": "pid=%s" % self.master_pid})
        return util.create_headers_response(302, extra_headers=extra)

    def register_master(self, quiz_name, common):
        m = game.GameMaster(quiz_name, common)
        common.pid_client[m.pid] = m
        common.join_number[m.join_number] = m
        return m


class homepage(Service):
    NAME = "/"  # This is the homepage

    def headers(self, extra):
        extra.update({"Location": "/home.html"})
        return util.create_headers_response(302, extra_headers=extra)


class answer(Service):
    NAME = "/answer"

    def __init__(self, letter, game):
        super(answer, self).__init__()
        game.answer = letter[0]


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
        try:
            util.remove_from_sysyem(common, pid)
        except AttributeError:
            pass


class check_test(TXTService):
    NAME = "/check_test"

    def __init__(self, join_number, common):
        super(check_test, self).__init__()
        self.data = int(join_number[0])
        self.common = common

    def content(self):
        return str((
            self.data in self.common.join_number and
            self.common.join_number[self.data].TYPE == "MASTER"
        ))


class check_name(TXTService):
    NAME = "/check_name"

    def __init__(self, join_number, name, common):
        super(check_name, self).__init__()
        self.data = int(join_number[0])
        self.name = name[0]
        self.common = common

    def content(self):
        ans = "False"
        if self.data in self.common.join_number:
            master = self.common.join_number[self.data]
            if master.TYPE == "MASTER":
                name_list = []
                for player in master.get_player_dict().values():
                    name_list.append(player.name)
                if self.name not in name_list:
                    ans = "True"
        return ans


class join(Service):
    NAME = "/join"

    def __init__(self, join_number, name, common, pid=None):
        super(join, self).__init__()
        if pid is not None:
            util.remove_from_sysyem(common, pid)
        self.player_pid = self.register_player(
            int(join_number[0]),
            name[0],
            common
        ).pid

    def headers(self, extra):
        extra.update({"Location": "/game.html",
                      "Set-Cookie": "pid=%s" % self.player_pid})
        return util.create_headers_response(302, extra_headers=extra)

    def register_player(self, join_number, name, common):
        g = game.GamePlayer(common.join_number[join_number], common, name)
        common.pid_client[g.pid] = g
        g.game_master.add_player(g.pid, g)
        return g


class check_test_exist(TXTService):
    NAME = "/check_test_exist"

    def __init__(self, quiz_name):
        super(check_test_exist, self).__init__()
        self._quiz_name = quiz_name[0]

    def content(self):
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


class get_join_number(TXTService):
    NAME = "/get_join_number"

    def __init__(self, pid, common):
        super(get_join_number, self).__init__()
        self._join_number = str(common.pid_client[pid].join_number)

    def content(self):
        return self._join_number


class get_information(TXTService):
    NAME = "/get_information"

    def __init__(self, game):
        super(get_information, self).__init__()
        self._game = game

    def content(self):
        return self._game.get_parser().get_information()


class set_timer_change(TXTService):
    NAME = "/set_timer_change"

    def __init__(self, game, new_time):
        super(set_timer_change, self).__init__()
        game.set_time_change(int(new_time[0]))


class check_timer_change(TXTService):
    NAME = "/check_timer_change"

    def __init__(self, game):
        super(check_timer_change, self).__init__()
        self._game = game

    def content(self):
        return str(self._game.check_timer_change())


class order_move_all_players(TXTService):
    NAME = "/order_move_all_players"

    def __init__(self, game):
        super(order_move_all_players, self).__init__()
        for player in game.get_player_dict().values():
            player.order_move_to_next_page()


class order_move_all_not_answered(TXTService):
    NAME = "/order_move_all_not_answered"

    def __init__(self, game):
        super(order_move_all_not_answered, self).__init__()
        for player in game.get_player_dict().values():
            if player.answer is None:
                player.order_move_to_next_page()


class check_move_next_page(TXTService):
    NAME = "/check_move_next_page"

    def __init__(self, game):
        super(check_move_next_page, self).__init__()
        self._game = game

    def content(self):
        ans = self._game.get_move_to_next_page()
        if ans:
            self._game.moved_to_next_page()
        return str(ans)


class move_to_next_question(TXTService):
    NAME = "/move_to_next_question"

    def __init__(self, game):
        super(move_to_next_question, self).__init__()
        self._game = game
        game.move_to_next_question()

    def content(self):
        return str(self._game.get_left_questions())


class get_question(TXTService):
    NAME = "/get_question"

    def __init__(self, game):
        super(get_question, self).__init__()
        self._game = game

    def content(self):
        return self._game.get_question()


class get_xml_leaderboard(TXTService):
    NAME = "/get_xml_leaderboard"

    def __init__(self, game):
        super(get_xml_leaderboard, self).__init__()
        self._game = game

    def content(self):
        return self._game.get_xml_leaderboard()


class check_move_question(TXTService):
    NAME = "/check_move_question"

    def __init__(self, game):
        super(check_move_question, self).__init__()
        self._game = game

    def content(self):
        return str(
            self._game.check_timer_change() or
            self._game.check_all_players_answered()
        )


class get_score(TXTService):
    NAME = "/get_score"

    def __init__(self, game):
        super(get_score, self).__init__()
        self._game = game

    def content(self):
        return "%d, %d" % (self._game.get_score(), self._game.get_place())


class start_question(TXTService):
    NAME = "/start_question"

    def __init__(self, game):
        super(start_question, self).__init__()
        game.start_question()
