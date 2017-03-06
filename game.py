import random


class Game(object):

    def __init__(self):
        super(Game, self).__init__()
        self._pid = random.randint(100000000, 999999999)

    @property
    def pid(self):
        return self._pid


class GameMaster(Game):
    NAME = "MASTER"

    def __init__(self, quiz_name):
        super(GameMaster, self).__init__()
        self._quiz = quiz_name
        self._players_list = {}  # {pid: GamePlayer}

    def add_player(self, new_pid, game_player):
        self._players_list[new_pid] = game_player

    def remove_player(self, pid):
        self._players_list.pop[pid]

    def get_player_list(self):
        return self._players_list


class GamePlayer(Game):
    NAME = "PLAYER"

    def __init__(self, master, name=None):
        super(GamePlayer, self).__init__()
        self._name = name
        self._game_master = master

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
