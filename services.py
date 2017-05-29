"""All the services get the method we need and return the data
"""
import os.path
from xml.etree import ElementTree

from . import base, game, util


class Service(base.Base):
    """Base class to all services"""

    ## The uri path needed to use this services
    NAME = 'base'

    def __init__(self):
        """Initialization"""
        super(Service, self).__init__()

        ## Did we read everything from read?
        self.finished_reading = False

        ## How much did we read from read
        self.read_pointer = 0
        self._content_page = None

    def content(self):
        """The body of the service"""
        return ""

    def close(self):
        """Do nothing, supposed to close an open file"""
        pass

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        if self._content_page is None:
            self._content_page = self.content()
        return util.create_headers_response(200,
                                            len(self._content_page),
                                            extra,
                                            ".html")

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


class XMLService(Service):
    """Service that return xml file"""

    def __init__(self):
        """Initialization"""
        super(XMLService, self).__init__()

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        if self._content_page is None:
            self._content_page = self.content()
        return util.create_headers_response(200,
                                            len(self._content_page),
                                            extra,
                                            ".xml")


class register_quiz(Service):
    """Register a quiz to a master and to the system
    GameMaster"""

    ## URI
    NAME = "/register_quiz"

    def __init__(self, quiz_name, common, base_directory, pid=None):
        """Initialization"""
        super(register_quiz, self).__init__()
        self._quiz_name = quiz_name[0]
        if pid is not None:
            util.remove_from_sysyem(
                common,
                pid,
            )
        g = self.register_master(quiz_name[0], common, base_directory)

        ## Master Player ID
        self.master_pid = g.pid

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        extra.update({"Location": "/quiz.html",
                      "Set-Cookie": "pid=%s" % self.master_pid})
        return util.create_headers_response(302, extra_headers=extra)

    def register_master(self, quiz_name, common, base_directory):
        """Creating GamePlayer object, registering it and returning it"""
        m = game.GameMaster(quiz_name, common, base_directory)
        common.pid_client[m.pid] = m
        common.join_number[m.join_number] = m
        return m


class homepage(Service):
    """Redirect to home.html"""

    ## URI
    NAME = "/"  # This is the homepage

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        extra.update({"Location": "/home.html"})
        return util.create_headers_response(302, extra_headers=extra)


class answer(Service):
    """Return the Answer from ["A", "B", "C", "D"]
    GamePlayer"""

    ## URI
    NAME = "/answer"

    def __init__(self, letter, game):
        """Initialization"""
        super(answer, self).__init__()
        game.answer = letter[0]


class getnames(XMLService):
    """Get all the names of all the player connected to the system
    GamMaster"""

    ## URI
    NAME = "/getnames"

    def __init__(self, game, common):
        """Initialization"""
        super(getnames, self).__init__()
        self._game = game
        self._common = common

    def content(self):
        """The content of the service"""
        root = ElementTree.Element("Root")
        for player in self._game.get_player_dict().values():
            name = player.name
            if name is not None:
                ElementTree.SubElement(root, "player", {"name": name})
        return util.to_string(root)


class diconnect_user(Service):
    """Disconnecting user from system
    GamePlayer"""

    ## URI
    NAME = "/diconnect_user"

    def __init__(self, pid, common, game):
        """Initialization"""
        super(diconnect_user, self).__init__()
        try:
            util.remove_from_sysyem(common, pid)
        except AttributeError:
            pass


class check_test(XMLService):
    """Check if a specific test is running"""

    ## URI
    NAME = "/check_test"

    def __init__(self, join_number, common):
        """Initialization"""
        super(check_test, self).__init__()

        ## Join number
        self.data = int(join_number[0])

        ## Common database
        self.common = common

    def content(self):
        """The content of the service"""
        return util.boolean_to_xml(
            self.data in self.common.join_number and
            self.common.join_number[self.data].TYPE == "MASTER"
        )


class check_name(XMLService):
    """Check if name not taken
    GamePlayer"""

    ## URI
    NAME = "/check_name"

    def __init__(self, join_number, name, common):
        """Initialization"""
        super(check_name, self).__init__()

        ## The join number
        self.data = int(join_number[0])

        ## The name
        self.name = name[0]

        ## Common library
        self.common = common

    def content(self):
        """The content of the service"""
        ans = "False"
        if self.data in self.common.join_number:
            master = self.common.join_number[self.data]
            if master.TYPE == "MASTER":
                name_list = []
                for player in master.get_player_dict().values():
                    name_list.append(player.name)
                if self.name not in name_list:
                    ans = "True"
        return util.boolean_to_xml(ans)


class join(Service):
    """Register player to master
    GamePlayer"""

    ## URI
    NAME = "/join"

    def __init__(self, join_number, name, common, pid=None):
        """Initialization"""
        super(join, self).__init__()
        if pid is not None:
            util.remove_from_sysyem(common, pid)

        ## Player ID
        self.player_pid = self.register_player(
            int(join_number[0]),
            name[0],
            common
        ).pid

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        extra.update({"Location": "/game.html",
                      "Set-Cookie": "pid=%s" % self.player_pid})
        return util.create_headers_response(302, extra_headers=extra)

    def register_player(self, join_number, name, common):
        """Creating GamePlayer object, registering it and returning it"""
        g = game.GamePlayer(common.join_number[join_number], common, name)
        common.pid_client[g.pid] = g
        g.game_master.add_player(g.pid, g)
        return g


class check_test_exist(XMLService):
    """Check if the test exist on the system
    GameMaster"""

    ## URI
    NAME = "/check_test_exist"

    def __init__(self, quiz_name, base_directory):
        """Initialization"""
        super(check_test_exist, self).__init__()
        self._quiz_name = quiz_name[0]
        self._base_directory = base_directory

    def content(self):
        """The content of the service"""
        return util.boolean_to_xml(
            os.path.isfile(
                os.path.normpath("%s\Quizes\%s.xml" %
                                 (self._base_directory,
                                  os.path.normpath(self._quiz_name))
                                 )
            )
        )


class new(Service):
    """Send you to / new.html"""

    ## URI
    NAME = "/new"  # This is the homepage

    def headers(self, extra):
        """Headers of the service, base if for any HTTP page"""
        extra.update({"Location": "/new.html"})
        return util.create_headers_response(302, extra_headers=extra)


class get_join_number(XMLService):
    """Return the join number to the game
    GameMaster"""

    ## URI
    NAME = "/get_join_number"

    def __init__(self, pid, common):
        """Initialization"""
        super(get_join_number, self).__init__()
        self._join_number = str(common.pid_client[pid].join_number)

    def content(self):
        """The content of the service"""
        root = ElementTree.Element("Root")
        ElementTree.SubElement(
            root, "join_number").text = self._join_number
        return util.to_string(root)


class get_information(XMLService):
    """Return the information about the question: It's name and how many
     questions
     GameMaster"""

    ## URI
    NAME = "/get_information"

    def __init__(self, game):
        """Initialization"""
        super(get_information, self).__init__()
        self._game = game

    def content(self):
        """The content of the service"""
        return self._game.get_information()


class set_timer_change(Service):
    """Set the timer for change part
    GameMaster\GamePlayer"""

    ## URI
    NAME = "/set_timer_change"

    def __init__(self, game, new_time):
        """Initialization"""
        super(set_timer_change, self).__init__()
        game.set_time_change(int(new_time[0]))


class check_timer_change(XMLService):
    """Check if the timer is ringing, got to 0
    GameMaster\Player"""

    ## URI
    NAME = "/check_timer_change"

    def __init__(self, game):
        """Initialization"""
        super(check_timer_change, self).__init__()
        self._game = game

    def content(self):
        """The content of the service"""
        return util.boolean_to_xml(self._game.check_timer_change())


class order_move_all_players(Service):
    """Order all the players to move to next part
    GameMaster"""

    ## URI
    NAME = "/order_move_all_players"

    def __init__(self, game):
        """Initialization"""
        super(order_move_all_players, self).__init__()
        for player in game.get_player_dict().values():
            player.order_move_to_next_page()


class order_move_all_not_answered(Service):
    """Order all the players who didn't answer to move to next part
    GameMaster"""

    ## URI
    NAME = "/order_move_all_not_answered"

    def __init__(self, game):
        """Initialization"""
        super(order_move_all_not_answered, self).__init__()
        for player in game.get_player_dict().values():
            if player.answer is None:
                player.order_move_to_next_page()


class check_move_next_page(XMLService):
    """Check if you need to move to next part
    GameMaster / GamePlayer"""

    ## URI
    NAME = "/check_move_next_page"

    def __init__(self, game):
        """Initialization"""
        super(check_move_next_page, self).__init__()
        self._game = game

    def content(self):
        """The content of the service"""
        return util.boolean_to_xml(self._game.get_move_to_next_page())


class moved_to_next_page(Service):
    """Confirmation that he moved to next part
    GameMaster / GamePlayer"""

    ## URI
    NAME = "/moved_to_next_question"

    def __init__(self, game):
        """Initialization"""
        super(moved_to_next_page, self).__init__()
        game.moved_to_next_page()


class move_to_next_question(XMLService):
    """Order move to next part"""

    ## URI
    NAME = "/move_to_next_question"

    def __init__(self, game):
        """Initialization"""
        super(move_to_next_question, self).__init__()
        self._game = game
        game.move_to_next_question()

    def content(self):
        """The content of the service"""
        root = ElementTree.Element("Root")
        ElementTree.SubElement(
            root,
            "question",
            {"number_of_questions": str(self._game.get_left_questions())}
        )
        return util.to_string(root)


class get_question(XMLService):
    """Return the question
    GameMaster"""

    ## URI
    NAME = "/get_question"

    def __init__(self, game):
        """Initialization"""
        super(get_question, self).__init__()
        self._game = game

    def content(self):
        """The content of the service"""
        return self._game.get_question()


class get_xml_leaderboard(XMLService):
    """Return the leaderboard"""

    ## URI
    NAME = "/get_xml_leaderboard"

    def __init__(self, game):
        """Initialization"""
        super(get_xml_leaderboard, self).__init__()
        self._game = game

    def content(self):
        """The content of the service"""
        return self._game.get_xml_leaderboard()


class check_move_question(XMLService):
    """Check if the user need to move to next question"""

    ## URI
    NAME = "/check_move_question"

    def __init__(self, game):
        """Initialization"""
        super(check_move_question, self).__init__()
        self._game = game

    def content(self):
        """The content of the service"""
        return util.boolean_to_xml(
            self._game.check_timer_change() or
            self._game.check_all_players_answered()
        )


class get_score(XMLService):
    """Return the score of the player who asked for it
    GamePlayer"""

    ## URI
    NAME = "/get_score"

    def __init__(self, game):
        """Initialization"""
        super(get_score, self).__init__()
        self._game = game

    def content(self):
        """The content of the service"""
        root = ElementTree.Element("Root")
        ElementTree.SubElement(
            root,
            "score_place",
            {
                "score": str(self._game.get_score()),
                "place": str(self._game.get_place())
            }
        )
        return util.to_string(root)


class start_question(Service):
    """Save the time the question started
    GameMaster"""

    ## URI
    NAME = "/start_question"

    def __init__(self, game):
        """Initialization"""
        super(start_question, self).__init__()
        game.start_question()


class get_answers(XMLService):
    """Return the right answers"""

    ## URI
    NAME = "/get_answers"

    def __init__(self, game):
        """Initialization"""
        super(get_answers, self).__init__()
        self._game = game

    def content(self):
        """The content of the service"""
        root = ElementTree.Element("Root")
        for letter in self._game.get_answers():
            ElementTree.SubElement(root, "answer", {"answer": letter})
        return util.to_string(root)


class get_title(XMLService):
    """Return the title of the question"""

    ## URI
    NAME = "/get_title"

    def __init__(self, game):
        """Initialization"""
        super(get_title, self).__init__()
        self._game = game

    def content(self):
        """The content of the service"""
        return self._game.get_title()
