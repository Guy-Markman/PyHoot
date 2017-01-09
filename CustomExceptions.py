class Disconnect(RuntimeError):
    """Represent an error that happend when someone disconnects"""

    def __init__(self):
        super(Disconnect, self).__init__("Disconnect")


class FinishedRequest(RuntimeError):
    """Represetn an error when we finish the request"""

    def __init__(self):
        super(Disconnect, self).__init__("Finished Request")
