from . import file_object


class Game(file_object):

    def __init__(self, quiz_name, base_directory):

        super(Game, self).__init__(quiz_name, base_directory)
