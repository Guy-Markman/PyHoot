"""The server class"""

import errno
import select
import socket
import traceback

from . import (async_io, base, client, common, common_events, constants,
               custom_exceptions, util)


class Server(base.Base):
    """The server class"""

    _database = {}
    _fd_socket = {}

    def __init__(
        self,
        buff_size,
        base_directory,
        io_mode
    ):
        """Initiliazator"""
        super(Server, self).__init__()
        self._buff_size = buff_size
        self._async_io_object = async_io.AsyncIO(io_mode)
        self._run = True
        self.logger.info("Initialized server, buff size '%d'", buff_size)
        self._base_directory = base_directory

        ## Init to common
        self.common = common.Common()

    def terminate(self):
        """Terminator for the system"""
        self._run = False

    def add_server(
        self,
        our_address
    ):
        """ Create the server side socket and add it to the database.
            our_address: Tupple of the address that the server will bind to.
                         format: (address, port)
        """
        s = util.creat_nonblocking_socket()
        s.bind(our_address)
        s.listen(1)
        self._add_to_databases(s)
        self.logger.info("Created server on address %s:%s", *our_address)

    def _add_to_databases(self, s, state=constants.SERVER):
        """
                Add the socket to the database. The structre will be:
                {socket :
                    {
                    "buff": The buffer will contain the data we need to send.
                    "state": The state of the socket, CLOSE, SERVER or CLIENT.
                    "fd": The file descriptor of the socket.
                    "client": Client Object for this socket
                    }
                }
        """
        if state not in (constants.CLOSE, constants.SERVER, constants.CLIENT):
            raise RuntimeError("State not found")
        self._database[s] = {
            "buff": "",
            "state": state,
            "fd": s.fileno(),
        }
        entry = self._database[s]
        if state == constants.CLIENT:
            entry["client"] = client.Client(
                s, self._buff_size, self._base_directory, self.common)
        self._fd_socket[s.fileno()] = s
        self.logger.debug(
            "The socket was added to the database, {'%s': '%s'}.",
            s,
            self._database[s])

    def _close_socket(self, s):
        """ Close the socket and remove it from from the database."""
        s.close()
        if s in self._database.keys():
            self._database.pop(s)
        self.logger.debug("The closing of the socket %s was successful.", s)

    def _change_to_close(self, entry):
        """Change the socket s to close state"""
        self.logger.debug("Current entry %s", entry)
        if entry["state"] == constants.CLIENT:
            entry["buff"] = entry["client"].get_send_buff()
            if entry["client"].get_file() is not None:
                entry["client"].get_file().close()
            entry.pop("client")
        entry["state"] = constants.CLOSE

    def _connect_socket(self, server):
        """Accept the socket to the system and add it to the database.
        """
        accepted = None
        try:
            accepted, addr = server.accept()
            accepted.setblocking(0)
            self._add_to_databases(accepted, state=constants.CLIENT)
            self.logger.info("Connected the socket from '%s:%s'", *addr)
        except Exception:
            self.logger.error("Exception ", exc_info=True)
            if accepted is not None:
                accepted.close()

    def start_server(self):
        """The main function of the class makes everything work"""
        while self._database:
            try:
                self._async_io_object.create_object()
                events = self._async_io_object.poll(self._database)
                self.logger.debug("Events \n%s", events)
                for fd, flag in events:
                    # taking care of all the sockets in rlist
                    s = self._fd_socket[fd]
                    if flag & common_events.CommonEvents.POLLIN:
                        socket_state = self._database[s]["state"]
                        if socket_state == constants.SERVER:
                            self.logger.debug("Server read")
                            self._connect_socket(s)
                        elif socket_state == constants.CLIENT:
                            self.logger.debug("Client Read")
                            self._database[s]["client"].recv()
                            self.logger.debug("finished receiving")

                    if flag & common_events.CommonEvents.POLLHUP:
                        raise custom_exceptions.Disconnect()

                    if flag & common_events.CommonEvents.POLLERR:
                        raise RuntimeError(
                            "Error in socket %s , closing it", s)

                    if flag & common_events.CommonEvents.POLLOUT:
                        entry = self._database[s]
                        if entry["state"] == constants.CLIENT:
                            self.logger.debug("Client send")
                            entry["client"].send()
                            if entry["client"].check_finished_request():
                                self.logger.info(
                                    "Completed reading the request for %s", s)
                                self._change_to_close(self._database[s])
                        if entry["state"] == constants.CLOSE:
                            self.logger.debug("Close send")
                            self.send(s)

                # This part checks whether the program needs to stop. If it
                # does, it starts the process of shuting down everything by
                # changing all the states to close
                if not self._run:
                    self.logger.debug("Closing all")
                    for s in self._database.keys():
                        self._change_to_close(self._database[s])

                # Closing every socket that is ready for close (sent everything
                # and in close mode)
                for s in self._database.keys():
                    entry = self._database[s]
                    if entry["state"] == constants.CLIENT:
                        if entry["client"].check_finished_request():
                            self.logger.info("Finished Request for %s", s)
                            self._change_to_close(self._database[s])
                    if entry["state"] == constants.CLOSE:
                        if entry["buff"] == "":
                            self._close_socket(s)
            except select.error as e:
                if e[0] != errno.EINTR:
                    self.logger.error(traceback.format_exc())
                    self._close_socket(s)
            except custom_exceptions.Disconnect:
                self.logger.info("%s disconneted", s)
                self._close_socket(s)
            except Exception:
                self.logger.critical(traceback.format_exc())
                self._close_socket(s)
        self.logger.debug("Finishing")
        self.logger.debug(self._database)

    def send(self, s):
        """Sending everything in case of a big error"""
        while self._database[s]["buff"]:
            try:
                sent = s.send(self._database[s]["buff"])
                self.logger.debug("sent %s", sent)
                self._database[s]["buff"] = self._database[s]["buff"][sent:]
            except socket.error as e:
                self.logger.error(traceback.format_exc())
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                else:
                    self.logger.debug("ERROR WOULD BLOCK")
                    break
        self.logger.debug("left %s", len(self._database[s]["buff"]))
