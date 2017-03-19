"""Game objects for the game, there is both player and master"""

import random

from . import constants, xmlparser


class Game(object):
    """Base game object, for the pid"""

    def __init__(self, common):
        super(Game, self).__init__()
        while True:
            pid = random.randint(constants.MIN_PID, constants.MAX_PID)
            if pid not in common.pid_client.keys():
                break
        self._pid = pid

    @property
    def pid(self):
        """The number of the object in the database"""
        return self._pid


class GameMaster(Game):
    NAME = "MASTER"

    def __init__(self, quiz_name, commmon):
        super(GameMaster, self).__init__(commmon)
        self._quiz = quiz_name
        self._players_list = {}  # {pid: GamePlayer}
        self._parser = xmlparser.XMLParser(quiz_name)

    def add_player(self, new_pid, game_player):
        self._players_list[new_pid] = game_player

    def remove_player(self, pid):
        self._players_list.pop(pid, None)

    def get_player_dict(self):
        return self._players_list

    def get_parser(self):
        return self._parser


class GamePlayer(Game):
    NAME = "PLAYER"

    def __init__(self, master, common, name=None):
        super(GamePlayer, self).__init__(common)
        self._name = name
        self._game_master = master  # Game object GameMaster
        self._move_to_next_page = False

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

    def order_move_to_next_page(self):
        self._move_to_next_page = True

    def moved_to_next_page(self):
        self._move_to_next_page = False
