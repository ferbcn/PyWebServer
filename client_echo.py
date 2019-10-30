# Python Web Server From Scratch

import socket

class TCPClient:
      host = '127.0.0.1'
      port = 8888

      def start(self):
          # create a socket object
          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # https://docs.python.org/2/library/socket.html

          # connect to host
          s.connect((self.host, self.port))

          message = "Hello World!"
          data_tx = message.encode()
          s.sendall(data_tx)
          data_rx = s.recv(1024)
          s.close()
          print(f"Data received: {data_rx.decode()}")

if __name__ == "__main__":
    myclient = TCPClient()
    myclient.start()
