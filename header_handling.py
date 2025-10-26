import config
import ProxyToServer
import DataRelay
import socket as se
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

        # print(f"Recieved header : {header}")
        return header, first_part_of_payload
    
def handle_client(client_socket):
    """
    Extract header, determine if it is CONNECT or other HTTP request
    """
    header, first_part_of_payload = recieve_header(client_socket)

    if not header:
        return
    
    header = header.replace(b'\r\n', b'\n')
    header_first_line = header.split(b'\n')[0].decode('utf-8', 'ignore')
    # header_first_line = header.split(b'\r\n')[0].decode('utf-8', 'ignore')
    header_parts = header_first_line.split()

    if len(header_parts)<3:
        return
    
    method, url, version = header_parts

    print(f">>> {method}\tURL : {url}\t Version : {version}")
    # print(f"\tURL : {url}\n\t Version : {version}")

    if method.upper() == "CONNECT":
        handle_connect(client_socket, url)

    else:
        handle_http(client_socket, header, first_part_of_payload, method, url)

def handle_connect(socket, url):
    """
    Create a TCP tunnel for CONNECT request
    """
    # try:
        # parse hostname and port from url - they are separated by :
    hostname, port_num = url.split(':')
    try:
        # parse hostname and port from url - they are separated by :
        port_num = int(port_num)
    except:
        print("Port number not present.")
        if url.lower().startswith('https://'):
            port_num = config.HTTPS_PORT
        else:
            port_num = config.HTTP_PORT
        print(f"Assigned port number : {port_num}")
        
    try:
        remote_conn = ProxyToServer.ProxyToServer(hostname, port_num)
        remote_socket = remote_conn.connect()
        socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        data_transfer = DataRelay.DataRelay(socket, remote_socket)
        data_transfer.relay()
    except ValueError:
        print(f"!!!! Oops !!! Invalid connect request, error in url : {url}")
        return
    except Exception as e:
        print(f"[!] Error in handle_connect: {e}")
        try:
            socket.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
        except:
            pass
        socket.close()
    
    # establish connection with dest server
    

def handle_http(socket, req_data, first_part_of_payload, method, url):
    print("Handling other kinds of http reqs")
   
    header = req_data.replace(b'\r\n', b'\n')
    header = header.decode('utf-8', 'ignore')
    header = req_data.decode('utf-8', 'ignore').split('\n')

    # header = header.split(b'\n')[0].decode('utf-8', 'ignore')
    # header = req_data.decode('utf-8', 'ignore').split('\r\n')
    host_header = next((h for h in header if h.lower().startswith('host:')), None)

    if not host_header:
        print("!!!! OOps. Could not find host header")
        return
        
    hostname = host_header.split(' ')[1]
    port_num = config.HTTP_PORT

    if ':' in hostname:
        hostname, port_num = hostname.split(':')
        try:
        # parse hostname and port from url - they are separated by :
            port_num = int(port_num)
        except:
            print("Port number not present.")
            if url.lower().startswith('https://'):
                port_num = config.HTTPS_PORT
            else:
                port_num = config.HTTP_PORT
            print(f"Assigned port number : {port_num}")
        # port_num = int(port_num)
        
        # ============ Modification to request header =============
    try :
        modified_headers = []
        first_line =  f"{method} {url} HTTP/1.0"
        modified_headers.append(first_line)
        
        for line in header[1:]:
            if line.lower().startswith("proxy-connection:"):
                # Replace with 'close'
                modified_headers.append("Proxy-Connection: close")
            elif not line.lower().startswith("connection:"):
                # Keep other headers
                modified_headers.append(line)
        modified_headers.append("Connection: close")

        # The header must end with a double CRLF
        modified_request = "\r\n".join(modified_headers).encode('utf-8') + b'\r\n\r\n'

        # Connect to remote host 
        remote_connection = ProxyToServer.ProxyToServer(hostname, port_num)
        remote_connection.connect()
        remote_connection.sock.sendall(modified_request)

        if first_part_of_payload:
            remote_connection.sock.sendall(first_part_of_payload)

        # transfer data between two sockets
        data_transfer = DataRelay.DataRelay(socket, remote_connection.sock)
        data_transfer.relay()

    except se.error as e:
        print(f"[!] Socket error during HTTP handling: {e}")
    except Exception as e:
        print(f"[!] Error during HTTP handling: {e}")
    finally:
        if 'remote_connection' in locals():
            remote_connection.close()



