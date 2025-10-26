import socket
import config
import header_handling

class SocketManager:
    '''
    Socket manager class to handle socket operations
    '''
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
        print(f"\nProxy server started on port {self.port}\n")


    def accept_connection(self):
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}\n")
            # returns the client socket and address, so that it can be handled by another component
            return client_socket, addr
        
    def close(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            print("Listening socket closed..............")


    