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

    def __init__(self, file_name):
        """ Creat FileObject
            Arguemnts:
                        file_name: The name of the file for the FileObject
                        buff_size: The size of the buff, default 1024
        """
        super(FileObject, self).__init__()
        self._file_name = file_name
        if not os.path.isfile(file_name):
            self.logger.error(traceback.format_exc())
            os.open(file_name, os.O_RDONLY)

        self._cursor_position = 0

    def read_buff(self, length):
        """ Open the file and read it up to length of the file"""
        if os.name == 'nt':
            fd = os.open(self._file_name, os.O_RDONLY | os.O_BINARY)
        else:
            fd = os.open(self._file_name, os.O_RDONLY)
        ret = ""
        try:
            os.lseek(fd, self._cursor_position, os.SEEK_SET)
            while len(ret) < length:
                buff = os.read(fd, length)
                if buff == "":  # got to the end of the file
                    break
                ret += buff
        finally:
            os.close(fd)
        self.logger.debug("read %s, length %s" % (ret, len(ret)))
        self._cursor_position += len(ret)
        return ret

    def check_read_all(self):
        """ Check if we read all the file"""
        file_length = os.stat(self._file_name).st_size
        self.logger.debug("read: %s, from %s" %
                          (self._cursor_position, file_length))
        return self._cursor_position == file_length

    def get_file_size(self):
        """ Return the size of the file"""
        return os.stat(self._file_name).st_size
