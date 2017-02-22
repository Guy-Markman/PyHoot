class Game(object):

    def __init__(self, quiz_name, base_directory, mode):
        super(Game, self).__init__()
        self._quiz_name = quiz_name
        self._base_directory = base_directory
        self._mode = mode
