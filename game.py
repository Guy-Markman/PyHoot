"""Game objects for the game, there is both player and master"""

import random


class Game(object):
    """Base game object, for the pid"""

    def __init__(self, common):
        super(Game, self).__init__()
        while True:
            pid = random.randint(100000000, 999999999)
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

    def add_player(self, new_pid, game_player):
        self._players_list[new_pid] = game_player

    def remove_player(self, pid):
        self._players_list.pop[pid]

    def get_player_dict(self):
        return self._players_list


class GamePlayer(Game):
    NAME = "PLAYER"

    def __init__(self, master, name=None):
        super(GamePlayer, self).__init__()
        self._name = name
        self._game_master = master  # Game object GameMaster

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
