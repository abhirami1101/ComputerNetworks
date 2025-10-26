import config
import select
from UtilsSocket import UtilsSocket

class DataRelay:
    ''' for bidirectional data transfer
        client <--> proxy <--> Server'''
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest
        self.buff_size = config.BUFFER_SIZE

    def relay(self):
        socks = [self.source, self.dest]
        try:
            while True:
                readable, _, _ = select.select(socks, [], []) # wait until one of the sockets is readable
                for sock in readable:
                    if sock is self.source:
                        # recvd_data = UtilsSocket.recv_until(self.source)
                        recvd_data = sock.recv(self.buff_size)
                        if not recvd_data:
                            return
                        self.dest.sendall(recvd_data)
                    elif sock is self.dest:
                        # recvd_data = UtilsSocket.recv_until(self.dest)
                        # cant use this as data relaying is for the rest of the data
                        recvd_data = sock.recv(self.buff_size) 
                        if not recvd_data:
                            return
                        self.source.sendall(recvd_data)
        except Exception as e:
            print(f"Data relay error: {e}")
        finally:
            self.source.close()
            self.dest.close()

    

