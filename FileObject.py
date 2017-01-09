import os
import traceback

import base


class FileObject(base.Base):
    """ This class reprsent an file that we read and send to the Server
        self._file_name = the name of the file
        self.buff_size = the buff size of the server
        self._cursor_position = The position of the cursor in the file,
                                represent how much we read already
    """

    def __init__(self, file_name, buff_size=1024):
        """ Creat FileObject
            Arguemnts:
                        file_name: The name of the file for the FileObject
                        buff_size: The size of the buff, default 1024
        """
        self._file_name = file_name
        if not os.path.isfile(file_name):
            self.logger.error(traceback.format_exc)
            os.open(file_name, os.O_RDONLY)

        self._cursor_position = 0

    def read_buff(self, length):
        """ Open the file and read it up to length of the file"""
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

    def check_read_all(self):
        """ Check if we read all the file"""
        return self.cursor_position == os.stat(self._file_name).st_size

    def get_file_size(self):
        """ Return the size of the file"""
        return os.stat(self._file_name).st_size
