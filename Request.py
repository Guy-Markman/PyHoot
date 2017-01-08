# Request that will be build over time
class Request(base.Base):
    
    def __init__():
        self._method = None
        self._uri = None
        self._headers ={}
    
    def set_method(method):
        self._method = method
    
    def get_method():
        return self._method
    
    def set_uri(uri):
        self._uri = uri

    def add_headers(header, content):
        self._headers[header] = content

    def get_all_header():
        return self._headers
    