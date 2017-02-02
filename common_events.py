import os
import select

import base


class CommontEvents(base.Base):
    POLLIN, POLLOUT, POLLERR, POLLHUP = (
        1, 4, 8, 16) if os.name == "nt" else (
        select.POLLIN, select.POLLOUT, select.POLLERR, select.POLLHUP)
