"""Select API for async_io."""
## @file select_object.py Select API for async_io.

import select

from . import base, common_events


class Select(base.Base):
    """
    Select API for async_io.
    Return events in the same protocol of Poll protocol
    Args:
        self._rlist: All the sockets that will be registered for reading
        self._wlist: All the sockets that will be registered for writing
        self._xlist: All the sockets that will be registered for errors
    """

    def __init__(self):
        """initialization"""
        super(Select, self).__init__()
        self._rlist = []
        self._wlist = []
        self._xlist = []

    def register(self, fd_socket, eventmask):
        """Add sockets to the lists it needs to be added
        Args:
            fd_socket: list of [file_descriptor of socket, socket]
            eventmask: The events we want to register it with (poll protocol)
        """
        socket = fd_socket[1]
        if eventmask & common_events.CommonEvents.POLLIN:
            self._rlist.append(socket)
        if eventmask & common_events.CommonEvents.POLLOUT:
            self._wlist.append(socket)
        if eventmask & common_events.CommonEvents.POLLERR:
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
        return polled.items()
