import os
from xml.etree import ElementTree
from xml.dom import minidom

def main():
    settings = ElementTree.Element("settings")
    name = raw_input("Name of the quiz. ")
    n_questions  = raw_input("How many question in the quiz? ")
    ElementTree.SubElement(settings, 'name').text=name
    ElementTree.SubElement(settings, 'number_of_questions').text=n_questions
    print prettify(settings)

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8")
    

if __name__ == "__main__":
	main()