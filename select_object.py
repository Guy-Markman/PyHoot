import select

from . import base, common_events


class Select(base.Base):

    def __init__(self):
        super(Select, self).__init__()
        self._rlist = []
        self._wlist = []
        self._xlist = []

    def register(self, fd_socket, eventmask):
        socket = fd_socket[1]
        if eventmask & common_events.POLLIN:
            self._rlist.append(socket)
        if eventmask & common_events.POLLOUT:
            self._wlist.append(socket)
        if eventmask & common_events.POLLERR:
            self._xlist.append(socket)

    def poll(self):
        """Turn the results of a select into the format of poll"""
        rlist, wlist, xlist = select.select(
            self._rlist, self._wlist, self._xlist
        )
        self.logger.debug(
            "select to poll \n rlist %s\nwlist %s\n xlist %s",
            rlist, wlist, xlist
        )
        polled = {}
        for s in rlist + wlist + xlist:
            fd = s.fileno()
            if s in rlist:
                polled[fd] = common_events.CommonEvents.POLLIN
            if s in wlist:
                polled[fd] = common_events.CommonEvents.POLLOUT
            if s in xlist:
                polled[fd] = common_events.CommonEvents.POLLERR
        return polled.items
