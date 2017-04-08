import os
from xml.dom import minidom
from xml.etree import ElementTree

N_ANSWERS = 4


def main():
    root = ElementTree.Element("Root")
    ElementTree.SubElement(root, "Quiz", {
        "name": raw_input("Name of the quiz. "),
        "number_of_questions": raw_input("How many question in the quiz? ")
    })
    for question in root.find("./Quiz").attrib["number_of_questions"]:
        q = ElementTree.SubElement(
            root.find("./Quiz"), "Question", {
                "duration": raw_input("How long is this question? In seconds ")
            })
        ElementTree.SubElement(q, "Text").text = "<![CDATA[%s]]>" % (
            raw_input("What is the question? "))
        for answer in range(N_ANSWERS):
            ans = ElementTree.SubElement(
                q, "Answer")
            ans.text = raw_input("Enter the answer ")
            right_wrong = raw_input(
                "Is the answer right or wrong? (answer in true or false) ")
            if right_wrong == "true":
                ans.attrib["correct"] = "1"
    build = prettify(root)
    print build
    name = root.find("./Quiz").attrib["name"]
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


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    print "Start"
    return minidom.parseString(
        ElementTree.tostring(
            elem, 'utf-8')
    ).toprettyxml(encoding='utf-8')


if __name__ == "__main__":
    main()
