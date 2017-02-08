import os
import select

from . import base


class CommonEvents(base.Base):
    POLLIN, POLLOUT, POLLERR, POLLHUP = (
        1, 4, 8, 16) if os.name == "nt" else (
        select.POLLIN, select.POLLOUT, select.POLLERR, select.POLLHUP)
