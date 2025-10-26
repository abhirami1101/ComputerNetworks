import socket
import threading
import sys
import config

class ProxyServer:

    def __init__(self, port = config.PORT):
        self.host = config.HOST
        self.port = port
        self.running = True
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # to allow reusing the address
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(100)
        print(f"Proxy server started on port {self.port}")

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
            # start a new thread to handle the client connection
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()
        
    def close(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            print("Proxy server closed")

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

    