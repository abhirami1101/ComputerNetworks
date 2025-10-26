import socket
import threading

class ProxyServer:
    '''Proxy server that listens for incoming connections, 
    creates a new thread for each client that handles the 
    communication between the client and the server'''
    def __init__(self, port = 8080):
        self.host = '0.0.0.0'
        self.port = port
        self.running = True
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    