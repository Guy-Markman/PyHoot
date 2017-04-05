"""Game objects for the game, there is both player and master"""

import base64
import os
import random
import time

from . import constants, xmlparser


class Game(object):
    """Base game object, for the pid"""

    def __init__(self, common):
        super(Game, self).__init__()
        while True:
            pid = base64.b64encode(os.urandom(constants.LENGTH_COOKIE))
            if pid not in common.pid_client.keys():
                break
        self._pid = pid
        self._change_timer = None
        self._move_to_next_page = False

    @property
    def pid(self):
        """The number of the object in the database"""
        return self._pid

    def get_move_to_next_page(self):
        return self._move_to_next_page

    def order_move_to_next_page(self):
        self._move_to_next_page = True

    def moved_to_next_page(self):
        self._move_to_next_page = False

    def set_time_change(self, new_time):
        self._change_timer = time.time() + new_time

    def check_timer_change(self):
        print self._change_timer - time.time()
        print self._change_timer - time.time() < 0
        return self._change_timer - time.time() < 0


class GameMaster(Game):
    TYPE = "MASTER"

    def __init__(self, quiz_name, common):
        super(GameMaster, self).__init__(common)
        self._quiz = quiz_name
        self._players_list = {}  # {pid: {"player": GamePlayer, "_score":score}
        self._parser = xmlparser.XMLParser(quiz_name)
        while True:
            join_number = random.randint(constants.MIN_PID, constants.MAX_PID)
            if join_number not in common.join_number.keys():
                break
        print join_number
        self._join_number = join_number

    def add_player(self, new_pid, game_player):
        self._players_list[new_pid] = {"player": game_player, "_score": 0}

    def remove_player(self, pid):
        self._players_list.pop(pid, None)

    def get_player_dict(self):
        dict = {}
        for key in self._players_list:
            dict[key] = self._players_list[key]["player"]
        return dict

    def get_parser(self):
        return self._parser

    def _update_score(self):
        right_answers = self._parser.get_question_answers()
        time_stop = time.time()
        for pid in self._players_list:
            player = self._players_list["player"]
            if player.answer in right_answers:
                self._players_list[pid]["_score"] += (
                    constants.QUESTION_TIME -
                    int(round((time_stop - player.timeanswer) * 100)))

    def get_html_leaderboard(self):
        # self._update_score()
        # dic_score_name = {}
        # for pid in self._players_list:
        # player_score = self._players_list[pid]
        # dic_score_name.update({player_score["_score"]: player_score["player"
        # ].name})
        # body = ""
        return "WIP"

    def get_question(self):
        return self._parser.get_xml_question()

    def move_to_next_question(self):
        self._parser.moved_to_next_question()

    def get_left_questions(self):
        return self._parser.get_left_questions()

    @property
    def join_number(self):
        """The number of the object in the database"""
        return self._join_number


class GamePlayer(Game):
    TYPE = "PLAYER"

    def __init__(self, master, common, name=None):
        super(GamePlayer, self).__init__(common)
        self._name = name
        self._game_master = master  # Game object GameMaster
        self._answer = None
        self._time = 0

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def game_master(self):
        return self._game_master

    @game_master.setter
    def game_master(self, new):
        self._game_master = new

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, answer):
        self._answer = answer

    @property
    def timeanswer(self):
        return self._time

    @timeanswer.setter
    def timeanswer(self, new_time):
        self._time = new_time
