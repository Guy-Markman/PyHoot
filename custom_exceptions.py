class Disconnect(RuntimeError):
    """Represent an error that happend when someone disconnects"""

    def __init__(self):
        super(Disconnect, self).__init__("Disconnect")


class AccessDenied(RuntimeError):
    """Represent an error that happend when the user tries to access a file
    they are not allowed to access"""
    def __init__(self):
        super(AccessDenied, self).__init__("Access Denied")
