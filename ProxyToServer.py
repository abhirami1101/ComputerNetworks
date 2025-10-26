import socket

class ProxyToServer:
    '''Creates a TCP connection to the given host and port. 
    Returns a connected socket or raises an error.'''
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.timeout = 5

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            print(f"Connected to server {self.host}:{self.port}")
            return self.sock
        except socket.error as e:
            print(f"Error connecting to server {self.host}:{self.port} --- {e}")
            raise
