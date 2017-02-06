import select
from . import base
from . import common_events


class AsyncIO(base.Base):

    def __init__(self, protocol):
        super(AsyncIO, self).__init__()
        self.protocol = protocol

    # IN: THE WHOLE DATABASE!
    # OUT: events in poll format

    def _build_select(self):
        """build the three list (rlist, wlist, xlist) for select.select"""
        rlist = []
        wlist = []
        xlist = []
        for s in self._database.keys():
            entry = self._database[s]
            if entry["state"] == self.CLOSE:
                wlist.append(s)
            if entry["state"] == self.SERVER:
                rlist.append(s)
            if entry["state"] == self.CLIENT:
                cl = entry["client"]
                if cl.can_recv():
                    rlist.append(s)
                if cl.can_send():
                    wlist.append(s)
        self.logger.debug(
            "build select\n rlist %s\nwlist %s\n xlist %s",
            rlist, wlist, xlist
        )
        return rlist, wlist, xlist

    def _io_select(self):
        """Build select and use it"""
        rlist, wlist, xlist = self._build_select()

        return select.select(rlist, wlist, xlist)

    def _select_to_poll(self):
        """Turn the results of a select into the format of poll"""
        rlist, wlist, xlist = self._io_select()
        self.logger.debug(
            "select to poll \n rlist %s\nwlist %s\n xlist %s",
            rlist, wlist, xlist
        )
        polled = {}
        for s in rlist + wlist + xlist:
            fd = self._database[s]["fd"]
            if s in rlist:
                polled[fd] = common_events.CommonEvents.POLLIN
            if s in wlist:
                polled[fd] = common_events.CommonEvents.POLLOUT
            if s in xlist:
                polled[fd] = common_events.CommonEvents.POLLERR
        events = polled.items()
        return events

    def _build_poller(self):
        """Creat and register poll"""
        poller = select.poll()
        for entry in self._database.values():
            events = common_events.CommonEvents.POLLERR
            if entry["state"] == self.CLOSE:
                events |= common_events.CommonEvents.POLLOUT
            elif entry["state"] == self.SERVER:
                events |= common_events.CommonEvents.POLLIN
            elif entry["state"] == self.CLIENT:
                cl = entry["client"]
                if cl.can_recv():
                    events |= common_events.CommonEvents.POLLIN
                if cl.can_send():
                    events |= common_events.CommonEvents.POLLOUT
            self.logger.debug(
                "reistered %s with events %s",
                entry["fd"],
                events)
            poller.register(entry["fd"], events)
        return poller

    def _io_poller(self):
        """Build poll and use it"""
        return self._build_poller().poll()
