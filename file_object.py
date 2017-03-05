import os

import base


class FileObject(base.Base):
    """ This class reprsent an file that we read and send to the Server
        self._fd = the file descriptor of the file
        self.finished_reading: Did we finished reading the file?
    """
    NAME = "FILE"

    def __init__(self, file_name, base_directory):
        """ Creat FileObject
            Arguemnts:
                file_name: The name of the file for the FileObject
                base_directory: The base directory whice we will use for file
                                locations
        """
        super(FileObject, self).__init__()
        # Build the address and open the file
        self._fd = os.open(os.path.normpath('%s%s' % (
            base_directory, os.path.normpath(file_name))),
            os.O_RDONLY | os.O_BINARY
        )
        self.finished_reading = False

    def read_buff(self, length):
        """ Read the file up to length of the file"""

        ret = ""
        while len(ret) < length:
            buff = os.read(self._fd, length)
            if buff == "":  # got to the end of the file
                break
            ret += buff
        self.logger.debug("read %s, length %s", ret, len(ret))
        return ret

    def get_file_size(self):
        """ Return the size of the file"""
        return os.fstat(self._fd).st_size

    def close(self):
        os.close(self._fd)
