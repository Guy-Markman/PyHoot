import select

from . import base


class Poll(base.Base):
    """
    Poll protocol for async_io.
    Return events in Poll protocol
    Args:
        self._poll, the current Poll objects
    """

    def __init__(self):

        super(Poll, self).__init__()
        self._poll = select.poll()

    def register(self, fd_socket, eventmask):
        """Register a file descriptor
        Args:
            fd_socket: list of [file_descriptor of socket, socket]
            eventmask: The events we want to register it with (poll protocol)
        """
        self._poll.register(fd_socket[0], eventmask)

    def poll(self):
        """Do poll on the registered file descriptors"""
        return self._poll.poll()
