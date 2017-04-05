import os
from xml.etree import ElementTree

from . import util

N_ANSWERS = 4


def main():
    Root = ElementTree.Element("Root")
    ElementTree.SubElement(Root, "Quiz", {
        "name": raw_input("Name of the quiz. "),
        "number_of_questions": raw_input("How many question in the quiz? ")
    })
    for question in Root.find("./Quiz").attrib["number_of_questions"]:
        q = ElementTree.SubElement(
            Root.find("./Quiz"), {
                "duration": raw_input("How long is this question? ")
            })
        ElementTree.SubElement(q, "Text").text = "<![CDATA[%s]]>" % (
            raw_input("What is the question?"))
        for answer in range(N_ANSWERS):
            ans = ElementTree.SubElement(
                q, "Answer").text = raw_input("Enter the answer ")
            right_wrong = raw_input(
                "Is the answer right or wrong? (answer in true or false) ")
            if right_wrong == "true":
                ans.attrib["correct"] = "1"
    build = util.prettify(Root)
    print build
    name = Root.find("./Quiz").attrib["name"]
    try:
        fd = os.open("../Quizes/%s.xml" % name, os.O_CREAT | os.O_WRONLY)
        try:
            build = build[os.write(fd, build):]
        finally:
            os.close(fd)
    except OSError:
        fd = os.open("%s.xml" % name, os.O_CREAT | os.O_WRONLY)
        try:
            build = build[os.write(fd, build):]
        finally:
            os.close(fd)


if __name__ == "__main__":
    main()
