import socket
import config

class UtilsSocket:
    '''
    Utility class for socket operations
    '''
    # Nand: I have implemented a better method for this recv_until func. It is in header handling.py
    @staticmethod
    def recv_until(sock, delimiter = b'\r\n\r\n'):
        """
        recieves data from the socket
        and returns when the delimiter is found,
        this is for protocol parsing
        before real data flow statrts
        """
        data = b''
        while delimiter not in data:
            chunk = sock.recv(config.BUFFER_SIZE)
            if not chunk:
                break
            data += chunk
        return data
    
    @staticmethod
    def send_all(sock, data):
        ''' send all the bytes to socket'''
        total = 0
        while total < len(data):
            sent = sock.send(data[total:])
            if sent == 0:
                raise RuntimeError('Connection broken, data not sent!!')
            total += sent

    # should I add close socket method here?
    # should I add timeout method here?


    