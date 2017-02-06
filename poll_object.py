import select

from . import base


class Poll(base.Base):

    def __init__(self):
        super(Poll, self).__init__()
        self._poll = select.poll

    def register(self, fd, eventmask):
        self._poll.register(fd, eventmask)

    def poll(self):
        return self._poll.poll()
