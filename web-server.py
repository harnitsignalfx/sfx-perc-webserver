#!/usr/bin/env python
"""
Very simple HTTP server in python.

Usage::
    ./dummy-web-server.py [<port>]

Send a GET request::
    curl http://localhost

Send a HEAD request::
    curl -I http://localhost

Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost

"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from pyformance import counter, count_calls #, timer
from pyformance.registry import MetricsRegistry
#from pyformance.reporters import ConsoleReporter
import signalfx.pyformance
import os
import socket
import sys

registry = MetricsRegistry()
counter = registry.counter("http_get_requests")
#timer = registry.timer("time_calls")
default_dimensions = {'containerId':socket.gethostname()}

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    @count_calls
    def do_GET(self):
        #with timer.time():
        self._set_headers()
        message = "<html><body><h1>h1!</h1></body></html>"
        self.wfile.write(bytes(message, "utf8"))
        counter.inc()

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print (post_data) # <-- Print post data
        self._set_headers()
        
def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print ('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    if 'SF_TOKEN' in os.environ:
        print (os.environ['SF_TOKEN'])
    else:
        print ('Please add SF_TOKEN as an env variable')
        sys.exit(0)
    if 'SERVER_PORT' in os.environ:
        port = os.environ['SERVER_PORT']
    else:
        print ('Using default port (SERVER_PORT env variable) as 80')
        port = 80

    #reporter = ConsoleReporter(registry=registry,reporting_interval=1)
    #reporter.start()
    sfx = signalfx.pyformance.SignalFxReporter(token=os.environ['SF_TOKEN'],default_dimensions=default_dimensions,reporting_interval=1,registry=registry)
    sfx.start()
    
    run(port=port)
