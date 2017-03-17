from xml.etree import ElementTree  # NOT THE MOVIE!

from . import constants


class XMLParser(object):

    def __init__(self, file_name):
        self._root = ElementTree.parse("%s.xml" % file_name).getroot()
        self.question_number = 0
        self.file_name = file_name
        self._settings = self._root.find("settings")
        self._number_of_questions = int(self._settings.find(
            "number_of_questions").text)
        self._questions = self._root.find("questions")

    def get_question_number(self):
        return self.question_number

    def get_left_questions(self):
        return self._number_of_questions - self.question_number

    def get_html_start(self):
        name_of_quiz = self._settings.find("name").text
        return constants.BASE_HTTP % (
            "%s" % name_of_quiz,
            """<center>
               <font size = 7>%s</font>
               <br><br>
               <font size = 4>%s questions</font>
               <script>
               setTimeout(function() { window.location = "/question" }, 5000);
               </script>
               </center>
            """ % (name_of_quiz, self._number_of_questions)
        )
