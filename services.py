"""All the services get the method we need and return the data 
"""

import time
BASE_HTTP = """<HTML>
    <head>
        <title>%s</title>
    </head>
    <BODY>
        %s
    </BODY>
</HTML>"""
def clock():
    return BASE_HTTP % (clock.__name__, "local timezone %s\nUTC timezone%s" % (time.strftime("%z %H:%M:%S"), time.strftime("%H:%M:%S", time.gmtime())))
    