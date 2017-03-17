from xml.etree import ElementTree  # NOT THE MOVIE!

from . import constants


class XMLParser(object):

    def __init__(self, quiz_name):
        self._root = ElementTree.parse("%s.xml" % quiz_name).getroot()
        self.question_number = 0
        self.quiz_name = quiz_name
        self._settings = self._root.find("settings")
        self._number_of_questions = int(self._settings.find(
            "number_of_questions").text)
        self._questions = self._root.find("questions")

    def get_question_number(self):
        return self.question_number

    def get_left_questions(self):
        return self._number_of_questions - self.question_number

    def get_html_start(self):
        return constants.HTTP_VERSION % (
            "%s" % self._settings,
            ""
        )
