"""
# Python WebServer From Scratch serving html and images using only the socket library
# One thread (and one connecion at a time) and therefore we have a blocking server --> Solution: ASYNCHIO

Example HTTP response:
HTTP/1.1 200 OK
Server: Tornado/4.3
Date: Wed, 18 Oct 2017 14:19:11 GMT
Content-type: text/html; charset=UTF-8
Content-Length: 13

Hello, world!
"""

import os
import socket
import datetime
import mimetypes

class TCPServer:
    host = '127.0.0.1'
    port = 8888

    def start(self):
        # create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)
        host_port = s.getsockname()
        print(f"Listening on {host_port[0]}:{host_port[1]}")
        try:
            while True:
                conn, addr = s.accept()
                print("Connected by", addr)
                now = datetime.datetime.now()
                print ("Current date and time : ", now.strftime("%d-%m-%Y %H:%M:%S"))
                #receive request
                data = conn.recv(1024)
                response_line, response_headers, blank_line, response_body = self.handle_request(data.decode())
                #send response
                conn.sendall(response_line.encode())
                conn.sendall(response_headers.encode())
                conn.sendall(blank_line.encode())
                conn.sendall(response_body)
                conn.close()
                print(f"Connection closed.")
        except KeyboardInterrupt:
            print("Server closed. Bye.")


class HTTPServer(TCPServer):
    headers = {
            'Server': 'SuperServer',
        }

    status_codes = {
            200: 'OK',
            404: 'Not Found',
            501: 'Not Implemented',
        }

    def handle_request(self, data):
        request = HTTPRequest(data)
        try:
            handler = getattr(self, f'handle_{request.method}')
        except AttributeError:
            handler = self.HTTP_501_handler
        response = handler(request)
        return response

    def HTTP_501_handler(self, request):
        response_line = self.response_line(status_code=501)
        response_headers = self.response_headers()
        blank_line = "\r\n"
        text = "501 Not Implemented"
        response_body = f"<h1>{text}</h1>"
        print(text)
        resp = "%s%s%s%s" % (
                response_line,
                response_headers,
                blank_line,
                response_body
            )
        return resp


    def handle_OPTIONS(self, request):
        response_line = self.response_line(200)
        extra_headers = {'Allow': 'OPTIONS, GET'}
        response_headers = self.response_headers(extra_headers)
        blank_line = "\r\n"
        response_body = "\r\n"
        return response_line, response_headers, blank_line, response_body


    def handle_GET(self, request):
        filename = request.uri.strip('/') # remove the slash from URI
        # set default rout to index.html
        if not filename:
            filename = "index.html"
        filepath = os.getcwd() + '/static/' + filename
        print("HTTP GET: ", filename)
        #filepath = os.path.join(staticdir, filename)
        print("Opening file at: ", filepath)

        if os.path.exists(filepath):
            response_line = self.response_line(200)
            # find out a file's MIME type
            # if nothing is found, just send `text/html`
            content_type = mimetypes.guess_type(filepath)[0] or 'text/html'
            print("MIME-TYPE: ",content_type)

            if content_type == "image/jpeg":
                file_options = 'rb'
            else:
                file_options = 'r'

            with open(filepath, file_options) as f:
                response_body = f.read()
                file_size = os.stat(filepath).st_size

            extra_headers = {'Content-Type': content_type, 'Content-Length': file_size}
            response_headers = self.response_headers(extra_headers)
            print("HEADERS: ")
            print(response_headers)

            image_formats = ("image/png", "image/jpeg", "image/jpg")
            if not content_type in image_formats:
                response_body = response_body.encode()
            blank_line = "\r\n"

            return response_line, response_headers, blank_line, response_body

        else:
            blank_line = "\r\n"
            response_line = self.response_line(404)
            response_headers = self.response_headers()
            response_body = "<h1>404 Not Found</h1>"
            print(response_body)
            response_body = response_body.encode()

            return response_line, response_headers, blank_line, response_body


    def response_line(self, status_code):
        """Returns response line"""
        reason = self.status_codes[status_code]
        return "HTTP/1.1 %s %s\r\n" % (status_code, reason)


    def response_headers(self, extra_headers=None):
        """Returns headers
        The extra_headers can be a dict for sending
        extra headers for the current response
        """
        headers_copy = self.headers.copy()
        if extra_headers:
            headers_copy.update(extra_headers)
        new_headers = ""
        for key in headers_copy.keys():
            new_headers += f"{key}: {headers_copy[key]}\r\n"
        return new_headers


class HTTPRequest:
    def __init__(self, data):
        print("HTTP Request")
        self.method = None
        self.uri = None
        self.http_version = '1.1' # default to HTTP/1.1 if request doesn't provide a version
        self.headers = {}
        self.parse(data)

    def parse(self, data):
        lines = data.split('\r\n')
        request_line = lines[0]
        self.parse_request_line(request_line)

    def parse_request_line(self, request_line):
        words = request_line.split(' ')
        self.method = words[0]
        self.uri = words[1]

        if len(words) > 2:
            self.http_version = words[2]


if __name__ == "__main__":
    myserver = HTTPServer()
    myserver.start()
