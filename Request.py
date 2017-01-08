# Request that will be build over time
import base


class Request(base.Base):

    def __init__(self, method=None, uri=None):
        self._method = method
        self._uri = uri
        self._headers = {}

    def set_method(self, method):
        self._method = method

    def get_method(self):
        return self._method

    def set_uri(self, uri):
        self._uri = uri

    def add_header(self, header, content):
        self._headers[header] = content

    def get_all_header(self):
        return self._headers
