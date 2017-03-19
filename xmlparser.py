from xml.etree import ElementTree  # NOT THE MOVIE!

from . import constants, custom_exceptions


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

    def get_html_question(self):
        question = self._dic_questions[self.question_number]
        picture = question.find("picture").text
        dic_answers = {}
        for ans in question.findall("answer"):
            dic_answers.update({ans.attrib["number"]: ans.find("answer_text"
                                                               ).text})
        body = """<center>
            <h1>%s</h1>""" % question.find("question_text").text
        if picture != "":
            body += """
            <br><br><img src="%s" style="width:304px;height:228px;>
            """ % picture
        body += """<table style="width:50%">"""
        # Had to break it to two parts because of %
        body += """<tr>
            <td>A: %s</td>
            <td>B: %s</td>
        </tr>
        <tr>
            <td>C: %s</td>
            <td>D: %s</td>
        </tr>
        </table>
        """ % (dic_answers["A"], dic_answers["B"], dic_answers["C"],
               dic_answers["D"])

    def get_question_answers(self):
        right_answer = []
        for ans in self._dic_questions[self.question_number].findall("answer"):
            if ans.find("right_wrong").text == "true":
                right_answer.append(ans.attrib["number"])
        return right_answer

    def test_file(self, filename):
        """Making sure everything is OK with the file before we start usings it
        """
        try:
            root = ElementTree.parse("%s.xml" % filename).getroot()
            if root is None:
                raise Exception("No root")
            settings = root.find("settings")
            if settings is None:
                raise Exception("No settings")
            name = settings.find("name")
            if name is None:
                raise Exception("No name")
            number_of_questions = settings.find("number_of_questions")
            if (
                number_of_questions is None or
                not number_of_questions.text.isdigit() or
                int(number_of_questions.text) < 1
            ):
                raise Exception("No number of questions")
            questions = root.find("questions")
            if questions is None:
                raise Exception("No questions")
            question_list = questions.findall("question")
            dic_questions = []
            for q in question_list:
                if not q.attrib.isditig() or int(q.attrib) < 1:
                    raise Exception("One of the questions don't have a number")
                question_text = q.find("question_text")
                if question_text is None or question_text.text == "":
                    raise Exception("One of the questions don't have text")
                if q.find("picture") is None:
                    raise Exception(
                        "One of the questions don't have picture SubElement")
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
