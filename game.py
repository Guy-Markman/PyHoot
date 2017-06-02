## @package PyHoot.game
# Game objects for the game, there is both player and master
## @file game.py Implementation of @ref PyHoot.game


import base64
import os
import random
import time
from xml.etree import ElementTree

from . import constants, xmlparser


# Registration -> Opening -> Question -> Answer -> Leaderboard -> Question
# (number_of_questions > -1) -> Finish


class Game(object):
    """Base game object, for the pid"""

    def __init__(self, common):
        """initialization"""
        super(Game, self).__init__()
        while True:
            pid = base64.b64encode(os.urandom(constants.LENGTH_COOKIE))
            if pid not in common.pid_client.keys():
                break
        """the pid, mostly the cookie"""
        self._pid = pid

        """The time you need to change when using the timer"""
        self._change_timer = None

        """Do you need to move to the next part"""
        self._move_to_next_page = False

    @property
    def pid(self):
        """The number of the object in the database"""
        return self._pid

    def get_move_to_next_page(self):
        """Check if need to move to the next part"""
        return self._move_to_next_page

    def order_move_to_next_page(self):
        """Ordering moving to the next part"""
        self._move_to_next_page = True

    def moved_to_next_page(self):
        """Confirm that the user moved to the next part"""
        self._move_to_next_page = False

    def set_time_change(self, new_time):
        """Set time to change, for the timer"""
        self._change_timer = time.time() + new_time

    def check_timer_change(self):
        """Check if need to change, for the timer"""
        return self._change_timer - time.time() < 0


class GameMaster(Game):
    """Game object for Mastser, controller of the sytstem"""

    ## The type of the object, MASTER
    TYPE = "MASTER"

    def __init__(self, quiz_name, common, base_directory):
        """initialization"""
        super(GameMaster, self).__init__(common)

        """name of the quiz"""
        self._quiz = quiz_name

        """list of the players"""
        self._players_list = {}  # {pid: {"player": GamePlayer, "_score":score}

        """xmlparser object"""
        self._parser = xmlparser.XMLParser(quiz_name, base_directory)

        while True:
            join_number = random.randint(constants.MIN_PID, constants.MAX_PID)
            if join_number not in common.join_number.keys():
                break

        """Join number, the players enter it in 'Enter pid' to join"""
        self._join_number = join_number

        """The time the question started"""
        self._time = None

    def add_player(self, new_pid, game_player):
        """Adding new player for the master"""
        self._players_list[new_pid] = {"player": game_player, "_score": 0}

    def remove_player(self, pid):
        """Removing player from the system"""
        self._players_list.pop(pid, None)

    def get_player_dict(self):
        """Return dictionary of all the players"""
        dict = {}
        for key in self._players_list:
            dict[key] = self._players_list[key]["player"]
        return dict

    def get_score(self, pid):
        """Returning the score of specific player"""
        return self._players_list[pid]["_score"]

    def get_current_question_title(self):
        """Return the title of the current question"""
        return self._parser.get_current_question_title()

    def _update_score(self):
        """Updating the score of all the players"""
        right_answers = self._parser.get_question_answers()
        for pid in self._players_list:
            player = self._players_list[pid]["player"]
            if player.answer in right_answers:
                self._players_list[pid]["_score"] += self._time - player.time
            player.answer = None

    def get_xml_leaderboard(self):
        """Return the leaderboard"""
        self._update_score()
        dic_name_score = {}
        for pid in self._players_list:
            dic_name_score.update(
                {
                    self._players_list[pid]["player"].name:
                    self._players_list[pid]["_score"]

                }
            )
        dic_score_names = {}
        for name in dic_name_score:
            score = dic_name_score[name]
            if score in dic_score_names:
                dic_score_names[score].append(name)
            else:
                dic_score_names[score] = [name]
        root = ElementTree.Element("Root")
        score_sorted = sorted(dic_score_names, reverse=True)
        for i in range(min(5, len(dic_score_names))):
            score = score_sorted[i]
            for player in dic_score_names[score]:
                ElementTree.SubElement(
                    root, "Player", {
                        "name": player,
                        "score": str(score)
                    }
                )
        return ElementTree.tostring(root, encoding=constants.ENCODING)

    def get_place(self, pid):
        """Return the place of the player"""
        scores_by_place = []
        for p in self._players_list:
            scores_by_place.append(self._players_list[p]["_score"])
        # Remove doubles and sort
        return sorted(list(set(scores_by_place)), reverse=True).index(
            self._players_list[pid]["_score"]) + 1

    def get_question(self):
        """Return the question and it's answers"""
        return self._parser.get_xml_question()

    def get_information(self):
        """Return the information about the question: It's name and how many
         questions"""
        return self._parser.get_information()

    def move_to_next_question(self):
        """Moving to the next question, also encryp the answer into the picture,
        """
        self._parser.move_to_next_question()
        self._encryp()

    def get_left_questions(self):
        """Return how many questions left - 1"""
        return self._parser.get_left_questions()

    def start_question(self):
        """Start the question"""
        self._time = self._parser.get_duration_question() * 100 + int(
            time.time() * 100)

    def check_all_players_answered(self):
        """Check if all the players answered"""
        ans = True
        for p in self._players_list.values():
            p = p["player"]
            if p._answer not in ["A", "B", "C", "D"]:
                ans = False
                break
        return ans

    def get_answers(self):
        """Return the right answers as A,B,C,D"""
        return self._parser.get_question_answers()

    def _get_picture(self):
        """Get the name of the picture file in the qustion
        @return Picture name (string) if available, else return None"""
        question = ElementTree.fromstring(
            self.get_question).find("./Text").text
        if "img" not in question:
            return None
        question = question[question.index("<img"):]
        question = question[0:question.index("/>") + len("/>")]
        question = question[question.index("src=") + len("src=") + 1:]
        question = question[:question.index('"')]
        return question

    def _enrypt(self):
        """Encrypt the answer in the picture"""
        picture = self._get_picture()
        if picture is None:
            return
        answer = self.get_answers[0].replace()
        fd = os.open(picture, os.O_RDWR | os.O_APPEND | os.O_BINARY)
        try:
            os.write(fd, answer)
        finally:
            os.close(fd)

    def _remove_answer_from_picture(self):
        """Remove the answer added in encrypt"""
        picture = self._get_picture()
        if picture is None:
            return
        with open(picture, 'rb+') as fd:
            fd.seek(-1, os.SEEK_END)
            fd.truncate()

    @property
    def join_number(self):
        """The number of the object in the database"""
        return self._join_number


class GamePlayer(Game):
    """Game object for player"""

    ## The type of the object, player
    TYPE = "PLAYER"

    def __init__(self, master, common, name=None):
        """Initialization"""
        super(GamePlayer, self).__init__(common)
        self._name = name
        self._game_master = master  # Game object GameMaster
        self._answer = None
        self._time = None

    def get_score(self):
        """Return the score of the player"""
        return self._game_master.get_score(self._pid)

    def get_place(self):
        """Return the place of the player"""
        return self._game_master.get_place(self._pid)

    def get_title(self):
        """Return the title of the question"""
        return self._game_master.get_current_question_title()

    @property
    def name(self):
        """Property name, the name of the player"""
        return self._name

    @name.setter
    def name(self, name):
        """Settter for property name"""
        self._name = name

    @property
    def game_master(self):
        """Property game_master, the master of this player"""
        return self._game_master

    @game_master.setter
    def game_master(self, new):
        """Settter for property game_master"""
        self._game_master = new

    @property
    def answer(self):
        """Property answer, the answer of this player"""
        return self._answer

    @answer.setter
    def answer(self, answer):
        """Settter for property answer"""
        if answer in ["A", "B", "C", "D"] or answer is None:
            self._answer = answer
            self._time = int(time.time() * 100)
        else:
            raise Exception("Answer not allowd")

    @property
    def time(self):
        """property time, when the player answered"""
        return self._time

    @time.setter
    def time(self, new_time):
        """Settter for property answer"""
        self._time = new_time
