from xml.etree import ElementTree

from . import constants, custom_exceptions, util

#  TODO: change all the x-path

class XMLParser(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self._root = ElementTree.parse(
            "PyHoot\Quizes\%s.xml" % file_name).getroot()
        self.question_number = 0  # 0 Represent the starting page
        self.file_name = file_name
        self._settings = self._root.find("settings")
        self._number_of_questions = int(self._settings.find(
            "number_of_questions").text)
        self._dic_questions = {}
        for q in self._root.find("questions").findall("question"):
            self._dic_questions.update({int(q.attrib["number"]): q})

    def get_question_number(self):
        return self.question_number

    def get_left_questions(self):
        return self._number_of_questions - self.question_number

    def get_information(self):
        return util.prettify(self._settings)

    def get_html_start(self):
        name_of_quiz = self._settings.find("name").text
        return constants.BASE_HTTP % (
            "%s" % name_of_quiz,
            """<center>
               <font size = 7>%s</font>
               <br><br>
               <font size = 4>%s questions</font>
               </center>
            """ % (name_of_quiz, self._number_of_questions)
            # <script>
            # setTimeout(function() { window.location = "/question" }, 5000);
            #                </script>
        )

    def get_xml_question(self):
        question = self._dic_questions[self.question_number]
        for ans in question.findall("answer"):
            ans.remove(ans.find("right_wrong"))
        return util.prettify(question)

    def get_question_answers(self):
        right_answer = []
        for ans in self._dic_questions[self.question_number].findall("answer"):
            if ans.find("right_wrong").text == "true":
                right_answer.append(ans.attrib["number"])
        return right_answer

    def test_file(self, filename):
        """Making sure everything is OK with the file before we start usings it
        """
        #  TODO: finish this
        try:
            root = ElementTree.parse("%s.xml" % filename).getroot()
            if root is None:
                raise Exception("No Root")
            settings = root.find("./Quiz").attrib
            if "name" in settings and "number_of_questions" in settings:
                raise Exception("Missings settings")
            number_of_questions = settings.attrib["number_of_questions"]
            if (
                not number_of_questions.text.isdigit() or
                int(number_of_questions.text) < 1
            ):
                raise Exception("No number of questions")
            question_list = root.findall("./Quiz/Question")
            
            
            
            
            dic_questions = []
            for q in question_list:
                if (
                    "duration" in q.attrib and
                    q.attrib["duration"] is digit
                    and int(q.attrib["duration"]) > 0
                ):
                    raise Exception("Missing duration")
                if q.find("Text") is 
                answers = q.findall("answer")
                if len(answers) != 4:
                    raise Exception(
                        "One of the questions too much \ not enough answers")
                dic_answers = []
                for ans in answers:
                    answer_text = ans.find("answer_text")
                    if answer_text is None or answer_text.text == "":
                        raise Exception("One of the answers don't have text")
                    right_wrong = ans.find("right_wrong")
                    if (
                        right_wrong is None or
                        right_wrong.text not in ("true", "false")
                    ):
                        raise Exception(
                            """One of the answers have problem with the
                            right_wrong text""")
                    dic_answers.update(ans.attrib["number"])
                if dic_answers != ["A", "B", "C", "D"]:
                    raise Exception(
                        """There is a problem with of the answers of one of the
                         questions answers number""")
                dic_questions.append(int(q.attrib["number"]))

            if len(dic_questions) != int(number_of_questions.text):
                raise Exception("Missings questions")
            keys = dic_questions.keys()
            if (
                sorted(keys) != keys and
                keys[0] != 1 and
                keys[-1] != int(number_of_questions.text)
            ):
                raise Exception("Questions not in order")
        except Exception as e:
            raise custom_exceptions.CorruptXML(str(e))

    def moved_to_next_question(self):
        self.question_number += 1
