from . import base, constants, common_events, poll_object, select_object


class AsyncIO(base.Base):

    def __init__(self, protocol):
        super(AsyncIO, self).__init__()
        self.protocol = protocol
        self._protocol_object = None

    def register_all(self, database):
        for s in database.keys():
            entry = database[s]
            events = common_events.CommonEvents.POLLERR
            if entry["state"] == constants.CLOSE:
                events |= common_events.CommonEvents.POLLOUT
            elif entry["state"] == constants.SERVER:
                events |= common_events.CommonEvents.POLLIN
            elif entry["state"] == constants.CLIENT:
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

    def create_object(self):
        self._protocol_object = (
            poll_object.Poll() if self.protocol == "poll" else
            select_object.Select()
        )

    def poll(self, database):
        self.register_all(database)
        return self._protocol_object.poll()


