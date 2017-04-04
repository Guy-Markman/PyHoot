import os.path
from xml.etree import ElementTree

from . import constants, custom_exceptions


class XMLParser(object):

    def __init__(self, file_name):
        test_file("%s.xml" % file_name, "PyHoot\Quizes")
        self.file_name = file_name
        self._root = ElementTree.parse(
            "PyHoot\Quizes\%s.xml" % file_name).getroot()
        self.question_number = 0  # 0 Represent the starting page
        self.file_name = file_name

    def get_question_number(self):
        return self.question_number

    def get_left_questions(self):
        return (
            int(self._root.find(
                "./Quiz").attrib["number_of_questions"]) - self.question_number
        )

    def get_information(self):
        backup_root = self._root
        for question in backup_root.findall("./Quiz/Question"):
            backup_root.find("./Quiz").remove(question)
        return ElementTree.tostring(backup_root, encoding=constants.ENCODING)

    def get_xml_question(self):
        question = self._root.findall(
            "./Quiz/Question")[self.question_number - 1]
        for ans in question.findall("answer"):
            ans.remove(ans.find("right_wrong"))
        return ElementTree.tostring(question, encoding=constants.ENCODING)

    def get_question_answers(self):
        right_answer = []
        for ans in self._root.findall("./Quiz/Question")[
                self.question_number].findall(".s/Answer"):
            if (
                "correct" in ans.attrib and
                ans.attrib["correct"] == "1"
            ):
                right_answer.append(["A", "B", "C", "D"][self._root.findall(
                    "./Quiz/Question").index(ans)])
        return right_answer

    def moved_to_next_question(self):
        self.question_number += 1


def test_file(filename, base="."):
    """Making sure everything is OK with the file before we start usings it
    """
    #  TODO: finish this
    root = ElementTree.parse(
        os.path.normpath(os.path.join(base, filename))
    )
    if root is None:
        raise custom_exceptions.CorruptXML("No Root")
    settings = root.find("./Quiz").attrib
    if "name" not in settings or "number_of_questions" not in settings:
        raise custom_exceptions.CorruptXML("Missings settings")
    number_of_questions = settings["number_of_questions"]
    if (
        not number_of_questions.isdigit() or
        int(number_of_questions) < 1
    ):
        raise custom_exceptions.CorruptXML("No number of questions")
    question_list = root.findall("./Quiz/Question")
    for q in question_list:
        if (
            "duration" not in q.attrib or
            not q.attrib["duration"].isdigit() or
            not int(q.attrib["duration"]) > 0
        ):
            raise custom_exceptions.CorruptXML("Missing duration")
        if q.find("./Text") is None or q.find("./Text").text.strip() == "":
            raise custom_exceptions.CorruptXML(
                "Problem with the text of one of the questions")
        answers = q.findall("./Answer")
        if len(answers) != 4:
            raise custom_exceptions.CorruptXML(
                "One of the questions too much \ not enough answers")
        correct = 0
        for ans in answers:
            if (
                "correct" in ans.attrib and
                ans.attrib["correct"] == "1"
            ):
                correct += 1
        if correct < 1:
            raise custom_exceptions.CorruptXML(
                "One of the questions don't have right answer")
    for ans in root.findall("./Quiz/Question/Answer"):
        answer_text = ans.find("./Text")
        if answer_text is None or answer_text.text.strip() == "":
            raise custom_exceptions.CorruptXML(
                "One of the answers don't have text")

    if len(root.findall("./Quiz/Question")) != int(
            root.find("./Quiz").attrib["number_of_questions"]):
        raise custom_exceptions.CorruptXML("Missings questions")
