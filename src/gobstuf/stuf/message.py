from io import StringIO

import os
import xml.etree.ElementTree as ET

from xml.dom import minidom


class StufMessage:
    """Workable representation of a StUF message, based on ElementTree.

    If namespaces is not defined this class builds namespaces based on the input message to keep the representation
    consistent and readable, and to make searching through a known XML string easier.
    """

    def __init__(self, msg: str, namespaces=None):
        self.namespaces = namespaces
        self.tree = None
        self.load(msg)

    def load(self, msg: str):
        if not self.namespaces:
            self.set_namespaces(msg)
        self.tree = ET.fromstring(msg)

    def set_namespaces(self, msg):
        self.namespaces = dict([node for _, node in ET.iterparse(StringIO(msg), events=['start-ns'])])

        for prefix, url in self.namespaces.items():
            ET.register_namespace(prefix, url)

    def find_elm(self, elements_str: str, tree=None):
        if tree is None:
            tree = self.tree

        elements = elements_str.split(' ')
        elm = tree.find(elements[0], self.namespaces)

        if len(elements) > 1:
            next_elements = " ".join(elements[1:])
            return self.find_elm(next_elements, elm)
        else:
            return elm

    def set_elm_value(self, elements_str: str, value: str, tree=None):
        elm = self.find_elm(elements_str, tree)
        elm.text = value

    def get_elm_value(self, elements_str: str, tree=None):
        elm = self.find_elm(elements_str, tree)
        return elm.text

    def to_string(self):
        return ET.tostring(self.tree, encoding='unicode')

    def pretty_print(self):
        xml_string = minidom.parseString(ET.tostring(self.tree)).toprettyxml()

        # normalise newlines
        xml_string = os.linesep.join([s for s in xml_string.splitlines() if s.strip()])
        return xml_string