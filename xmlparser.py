from xml.etree import ElementTree  # NOT THE MOVIE!

from . import constants


class XMLParser(object):

    def __init__(self, file_name):
        self._root = ElementTree.parse("%s.xml" % file_name).getroot()
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
               <script>
               setTimeout(function() { window.location = "/question" }, 5000);
               </script>
               </center>
            """ % (name_of_quiz, self._number_of_questions)
        )

    def get_http_question(self):
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
        body += """<table style="width:50%">
        <tr>
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
