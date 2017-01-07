import os
import traceback

import base


# This class reprsent an file that we read and send to the Server
# name = the name of the file we want to send
# buff_size = the size of the buff on server


class FileObject(base.Base):

    def __init__(self, file_name, buff_size):
        self._file_name = file_name
        if not os.path.isfile(file_name):
            self.logger.error(traceback.format_exc)
            os.open(file_name, os.O_RDONLY)

        self._cursor_position = 0  # The curson position right now

    # open the file and read it up to length of the file
    def read_buff(self, length):
        fd = os.open(self._file_name, os.O_RDONLY)
        ret = None
        try:
            os.lseek(fd, self.cursor_position, os.SEEK_SET)
            while len(ret) < length:
                buff = os.read(fd, length)
                if buff == "":  # got to the end of the file
                    break
                ret += buff
        finally:
            os.close(fd)
        self.cursor_position += len(ret)
        return ret

    # Check if we finished reading
    def check_read_all(self):
        return self.cursor_position == os.stat(self._file_name).st_size
