"""
This module deals with the header handling
"""

def recieve_header(socket):
    """
    This function recieves the header from a socket
    Returns:
        a tuple: (header , first_part_of_payload)
    """

    header_buffer = b''
    while b'\r\n\r\n' not in header_buffer:
        header_part = socket.recv(1024)
        if not header_part:
            return None, None # client closed connection before sending full header
        header_buffer += header_part

        header_end_index = header_buffer.find(b'\r\n\r\n') + 4
        header = header_buffer[:header_end_index]
        first_part_of_payload = header_buffer[header_end_index:]

        return header, first_part_of_payload
    
def handle_client(client_socket):
    """
    Extract header, determine if it is CONNECT or other HTTP request
    """
    header, first_part_of_payload = recieve_header(client_socket)

    if not header:
        return
    
    header_first_line = header.split(b'\r\n')[0].decode('utf-8', 'ignore')
    header_parts = header_first_line.split()

    if len(header_parts)<3:
        return
    
    method, url, version = header_parts

    print(f">>> {method} {url}")

    if method.upper() == "CONNECT":
        print("deal connect")

    else:
        print(f"other method : {method}")