"""Common class, It is just a nice way to share databases with all the clients
"""
## @file common.py Common class, It is just a nice way to share databases


class Common(object):
    """Common class, It is just a nice way to share databases with all the clients
    """

    def __init__(self):
        """Initialization"""

        ## Dictionary of key of pid (integer_ and value of the client object
        ## (Clinet)
        self.pid_client = {}

        ## Dictionary of key of join number and value of client object (Client)
        self.join_number = {}
