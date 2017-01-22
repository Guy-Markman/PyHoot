import os

import base


class FileObject(base.Base):
    """ This class reprsent an file that we read and send to the Server
        self._file_name = the name of the file
        self.buff_size = the buff size of the server
        self._cursor_position = The position of the cursor in the file,
                                represent how much we read already
    """

    def __init__(self, file_name):
        """ Creat FileObject
            Arguemnts:
                        file_name: The name of the file for the FileObject
                        buff_size: The size of the buff, default 1024
        """
        super(FileObject, self).__init__()
        self._fd = os.open(file_name, os.O_RDONLY | os.O_BINARY)
        self.finished_reading = False

    def read_buff(self, length):
        """ Open the file and read it up to length of the file"""

        ret = ""
        while len(ret) < length:
            buff = os.read(self._fd, length)
            if buff == "":  # got to the end of the file
                break
            ret += buff
        self.logger.debug("read %s, length %s", ret, len(ret))
        return ret

    def check_read_all(self):
        """ Check if we read all the file"""
        return self.finished_reading

    def get_file_size(self):
        """ Return the size of the file"""
        return os.fstat(self._fd).st_size

    def close(self):
        os.close(self._fd)
