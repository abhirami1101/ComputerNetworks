import socket
<<<<<<< HEAD:Server.py
import threading
import sys
import config

class ProxyServer:

    def __init__(self, port = config.PORT):
        self.host = config.HOST
=======

class SocketManager:
    '''Socket manager class to handle socket operations'''
    def __init__(self, port = 8080):
        self.host = '0.0.0.0'
>>>>>>> 07ddc0ee1556ae4844d57c600b4a6917317e4300:SocketManager.py
        self.port = port
        self.running = True
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # to allow reusing the address
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(100)
        print(f"Proxy server started on port {self.port}")


    def accept_connection(self):
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
            # returns the client socket and address, so that it can be handled by another component
            return client_socket, addr
        
    def close(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            print("Listening socket closed")

    def handle_client(client_socket):
        """
        Handle a client request
        """
        try:
            request = client_socket.recv(config.BUFFER_SIZE)
            print(request)
            if not request:
                return
        except Exception as e:
            print(f"Caught up with an error {e}")

    