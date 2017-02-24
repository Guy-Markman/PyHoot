import random


class Game(object):

    def __init__(self):
        super(Game, self).__init__()
        self._pid = random.randint(1000000000, 9999999999)

    def get_pid(self):
        return self._pid


class GameMaster(Game):
    NAME = "MASTER"

    def __init__(self, quiz_address):
        super(GameMaster, self).__init__()
        self._quiz = quiz_address
        self._players_list = {}  # {pid: GamePlayer}

    def add_player(self, pid, game_player):
        self._players_list[pid] = game_player


class GamePlayer(Game):
    NAME = "PLAYER"

    def __init__(self, master, name=None):
        super(GamePlayer, self).__init__()
        self._name = name
        self._game_master = master

    def set_name(self, new_name):
        self._name = new_name
