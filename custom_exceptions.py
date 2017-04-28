class Disconnect(RuntimeError):
    """Represent an error that happend when someone disconnects"""

    def __init__(self):
        super(Disconnect, self).__init__("Disconnect")


class CorruptXML(RuntimeError):

    def __init__(self, message):
        super(CorruptXML, self).__init__("Corrupt XML: %s" % message)
