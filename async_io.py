from . import base, common_events, poll_object, select_object


class AsyncIO(base.Base):

    def __init__(self, protocol):
        super(AsyncIO, self).__init__()
        self.protocol = protocol
        self._protocol_object = ()
    # IN: THE WHOLE DATABASE!
    # OUT: events in poll format

    def register_all(self, database):
        for s in database.keys():
            entry = database[s]
            events = events = common_events.CommonEvents.POLLERR
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
            self._protocol_object.register([entry["fd"], s], events)

    def poll(self):
        self.register_all()
        return self._protocol_object.poll()

    def creat_object(self):
        self._protocol_object = (
            poll_object.Poll() if self.protocol == "poll" else
            select_object.Select
        )
