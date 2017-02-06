from . import base
from . import common_events


class Select(base.Base):

    def __init__(self):
        super(Select, self).__init__()
        self._rlist = []
        self._wlist = []
        self._xlist = []

    def register(self, socket, eventmask):
        if eventmask & common_events.POLLIN:
            self._rlist.append(socket)
        if eventmask & common_events.POLLOUT:
            self._wlist.append(socket)
        if eventmask & common_events.POLLERR:
            self._xlist.append(socket)
