import os
import string
from xml.etree import ElementTree

from . import util

N_ANSWERS = 4


def main():
    quiz = ElementTree.Element("quiz")
    settings = ElementTree.SubElement(quiz, "settings")
    name = raw_input("Name of the quiz. ")
    n_questions = raw_input("How many question in the quiz? ")
    ElementTree.SubElement(settings, 'name').text = name
    ElementTree.SubElement(settings, 'number_of_questions').text = n_questions
    questions = ElementTree.SubElement(quiz, "questions")
    for x in range(int(n_questions)):
        q = ElementTree.SubElement(questions, "question", number=str(x + 1))
        ElementTree.SubElement(q, "question_text").text = raw_input(
            "What is the question? ")
        ElementTree.SubElement(q, "picture").text = raw_input(
            "Picture name. Must include extension. Leave Blunk for nothing.")
        for z in range(N_ANSWERS):
            answer = ElementTree.SubElement(
                q, "answer", number=string.ascii_uppercase[z])
            ElementTree.SubElement(
                answer, "answer_text").text = raw_input("Enter the answer ")
            ElementTree.SubElement(answer, "right_wrong").text = raw_input(
                "Is the answer right or wrong? (answer in true or false)")
    build = util.prettify(quiz)
    print build
    try:
        fd = os.open("../Quizes/%s.xml" % name, os.O_CREAT | os.O_WRONLY)
    except OSError:
        fd = os.open("%s.xml" % name, os.O_CREAT | os.O_WRONLY)
    try:
        while build:
            build = build[os.write(fd, build):]
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
