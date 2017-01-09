import base


class Request(base.Base):
    """ Request that will be build over time, contain the method, uri and headers
        Arguements:
                    self._method, the method of the request (in the current
                                 version only GET is supported)
                    self._uri, the uri of the requested file
                    self._headers, a dictionary that contain the name of the
                                  header as key and the header itself as value
    """

    def __init__(self, method=None, uri=None):
        """ Request that will be build over time, contain the method, uri
            and headers
            Arguments:
                        method, the method of the request (in the current
                                version only GET)
                        uri, the uri of the requested file
        """
        self._method = method
        self._uri = uri
        self.headers = {}

    def set_method(self, method):
        """ Set self._method
            Arguments:
                        method, the new method
        """
        self._method = method

    def get_method(self):
        """ Return self.method"""
        return self._method

    def set_uri(self, uri):
        """ Set self.uri
            Arguments:
                        uri, the new uri
        """
        self._uri = uri

    def add_header(self, header, content):
        """ Add header
            Arguemnts:
                        header, the name of the header
                        content, the content of the header
        """
        self._headers[header] = content

    def get_all_header(self):
        """ Return self._headers"""
        return self._headers

    def remove_header(self, header):
        """ Remove a header by its name
            Arguemtns:
                        header, the name of the header
        """
        self._header.pop(header)
