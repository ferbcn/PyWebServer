"""
# Python WebServer From Scratch serving html and images using streams and asyncio library
"""

import sys
import os
import datetime
import mimetypes
import asyncio
import time


# Asynchronous (aka non-blocking) webserver using asyncio
class TCPServerAsync():

    def __init__(self):
        pass

    async def handle_client(self, reader, writer):
        print("Connection received!")
        now = datetime.datetime.now()
        print ("Current date and time : ", now.strftime("%d-%m-%Y %H:%M:%S"))
        data = await reader.read(100)
        print("Data received!")
        print(data)
        # TO-DO handle timeout if client opens connection but doesnt send any data or request
        request = HTTPRequest(data.decode())
        try:
            command = request.uri.strip('/')
        except AttributeError:
            command = None
        print("URI: ", command)
        print('Sending respose...')
        if command == "quit":
            response_line, response_headers, blank_line, response_body = self.handle_shutdown()
        else:
            response_line, response_headers, blank_line, response_body = self.handle_request(data.decode())

        response_data = response_line.encode() + response_headers.encode() + blank_line.encode()
        writer.write(response_data)
        writer.write(response_body)
        await writer.drain()
        writer.close()
        print('Connection closed.')

        if command == "quit":
            print('Closing server...')
            self.server.close()
            await self.server.wait_closed()

    async def start(self, host, port):
        self.server = await asyncio.start_server(
            self.handle_client, host, port)

        addr = self.server.sockets[0].getsockname()
        print(f'Asynchronous server started. Listening on {addr[0]}:{addr[1]}')

        async with self.server:
            try:
                await self.server.serve_forever()
            except Exception as e:
                pass
            finally:
                print('Server closed!')


class HTTPServer(TCPServerAsync):
    headers = {
            'Server': 'AsyncServer',
        }

    status_codes = {
            200: 'OK',
            404: 'Not Found',
            501: 'Not Implemented',
            503: 'Not Available',
        }

    def handle_request(self, data):
        request = HTTPRequest(data)
        try:
            handler = getattr(self, f'handle_{request.method}')
        except AttributeError:
            handler = self.HTTP_501_handler
        response = handler(request)
        return response

    def handle_shutdown(self):
        response_line = self.response_line(status_code=503)
        response_headers = self.response_headers()
        blank_line = "\r\n"
        text = "Server shutdown. Bye!"
        response_body = f"<h1>{text}</h1>".encode()
        print(text)
        return response_line, response_headers, blank_line, response_body

    def HTTP_501_handler(self, request):
        response_line = self.response_line(status_code=501)
        response_headers = self.response_headers()
        blank_line = "\r\n"
        text = "501 Not Implemented"
        response_body = f"<h1>{text}</h1>".encode()
        print(text)
        return response_line, response_headers, blank_line, response_body


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

            image_formats = ("image/png", "image/jpeg", "image/jpg", "image/x-icon")

            if content_type in image_formats:
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

            image_formats = ("image/png", "image/jpeg", "image/jpg", "image/x-icon")
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
        return f"HTTP/1.1 {status_code} {reason}\r\n"


    def response_headers(self, extra_headers=None):
        """Returns headers
        The extra_headers can be a dict for sending
        extra headers for the current response
        """
        headers_copy = self.headers.copy() # make a local copy of headers
        if extra_headers:
            headers_copy.update(extra_headers)
        new_headers = ""
        for key in headers_copy.keys():
            new_headers += f"{key}: {headers_copy[key]}\r\n"
        return new_headers


# helper class for parsing http request
class HTTPRequest:
    def __init__(self, data):
        self.method = None
        self.uri = None
        self.http_version = '1.1' # default to HTTP/1.1 if request doesn't provide a version
        self.headers = {} # a dictionary for headers
        # call self.parse method to parse the request data
        self.parse(data)

    def parse(self, data):
        lines = data.split('\r\n')
        request_line = lines[0]
        words = request_line.split(' ')
        #print("WORDS: ", words)
        self.method = words[0]
        try:
            self.uri = words[1]
        except IndexError:
            pass

        if len(words) > 2:
            self.http_version = words[2]


if __name__ == "__main__":

    try:
        script, host, port = sys.argv
    except ValueError:
        host='127.0.0.1'
        port='8888'

    myserver = HTTPServer()
    try:
        asyncio.run(myserver.start(host, port))
    except KeyboardInterrupt:
        print("Ctrl-C pressed. Bye!")
