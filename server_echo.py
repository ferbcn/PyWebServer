# Python Web Server From Scratch

import socket

class TCPServer:
      host = '127.0.0.1'
      port = 8888

      def start(self):
          # create a socket object
          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # https://docs.python.org/2/library/socket.html

          # bind to address and port
          s.bind((self.host, self.port))

          #listen for connections
          s.listen(1)

          while True:
              try:
                  #accept connections
                  conn, addr = s.accept()
                  print (f"Connection received by {addr}")
                  data = conn.recv(1024)
                  conn.sendall(data)
                  conn.close()
              except KeyboardInterrupt:
                  break



if __name__ == "__main__":
    myserver = TCPServer()
    myserver.start()
