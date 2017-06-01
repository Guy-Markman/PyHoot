## @package PyHoot.async_io
# AsyncIO (with select_object or poll_object)
## @file async_io.py Implementation of @ref PyHoot.async_io


from . import base, common_events, constants, poll_object, select_object


class AsyncIO(base.Base):
    """AsyncIO object (with select_object or poll_object).
    Return fd like poll no matter what API we use.
    Args:
        self.protocol= the API we are using
        self._protocol= the object we will use, depent on API.
                        if we use poll, poll we will have poll_object,
                        if we use select, select_object
    """

    def __init__(self, protocol):
        """Create AsyncIO object
        Parameters:
            protocol, the protocol we will use
        """
        super(AsyncIO, self).__init__()

        ## The API we will use
        self.protocol = protocol

        """API Object"""
        self._protocol_object = None

    def register_all(self, database):
        """Register all the sockets in the database"""
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
        """Create or re - create the protocol object
        Args:
            database, the database with all the socket we will use
        """
        self._protocol_object = (
            poll_object.Poll() if self.protocol == "poll" else
            select_object.Select()
        )

    def poll(self, database):
        """Register all the sockets in database and return file descriptor we
        can use
        Args:
            database, the database with all the socket we will use

        Return:
            events in the same protocol of poll
        """
        self.register_all(database)
        return self._protocol_object.poll()
