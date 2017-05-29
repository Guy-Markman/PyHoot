"""Events for async_io"""

import os
import select

from . import base


class CommonEvents(base.Base):
    """Setting up Common event for asyncIO"""

    ## os.name != 'nt', not windows
    linux = os.name != 'nt'

    ## POLLIN - Events of read
    POLLIN = 1
    if linux:
        POLLIN = select.POLLIN

    ## POLLOUT - Events of write
    POLLOUT = 4
    if linux:
        POLLOUT = select.POLLOUT

    ## POLLERR - Events of error
    POLLERR = 8
    if linux:
        POLLERR = select.POLLERR

    ## POLLHUP - Events of disconnecting
    POLLHUP = 16
    if linux:
        POLLHUP = select.POLLHUP
