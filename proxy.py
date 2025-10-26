import socket
import threading
import sys
import select

# --- Configuration ---
HOST = '127.0.0.1'  # localhost
PORT = 8080         # Port for the proxy to listen on
BUFFER_SIZE = 4096
MAX_CLIENTS = 10

def main():
    """ The main function to set up the server socket and listen for clients. """
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CLIENTS)
        print(f"[*] Proxy server listening on {HOST}:{PORT}")
    except Exception as e:
        print(f"[!] Error setting up server socket: {e}")
        sys.exit(1)

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        
        # Create a new thread to handle the client connection
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def handle_client(client_socket):
    """ Handles a single client connection, determining if it's CONNECT or standard HTTP. """
    try:
        # Read the initial request from the browser
        request_data = client_socket.recv(BUFFER_SIZE)
        print(request_data)
        if not request_data:
            return

        # Parse the first line to get method, URL, and version
        first_line = request_data.split(b'\r\n')[0].decode('utf-8', 'ignore')
        parts = first_line.split()
        if len(parts) < 3:
            return

        method, url, version = parts
        
        # --- Print the required output format ---
        print(f">>> {method} {url}")

        if method.upper() == 'CONNECT':
            handle_connect(client_socket, url)
        else:
            handle_http(client_socket, request_data, method, url)
            
    except Exception as e:
        print(f"[!] Error handling client: {e}")
    finally:
        client_socket.close()

def handle_connect(client_socket, url):
    """ Handles HTTPS CONNECT requests by setting up a TCP tunnel. """
    try:
        # Parse hostname and port from the URL (e.g., "www.google.com:443")
        hostname, port_str = url.split(':')
        port = int(port_str)
    except ValueError:
        print(f"[!] Invalid CONNECT request for URL: {url}")
        return

    try:
        # Establish connection with the destination server
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((hostname, port))
        
        # Send a success response back to the browser
        success_response = b"HTTP/1.1 200 OK\r\n\r\n"
        client_socket.sendall(success_response)
        
        # Start the bidirectional data transfer (tunneling)
        transfer_data(client_socket, remote_socket)
        
    except socket.error as e:
        print(f"[!] Failed to connect to {hostname}:{port} -> {e}")
        # Send a failure response back to the browser
        failure_response = b"HTTP/1.1 502 Bad Gateway\r\n\r\n"
        client_socket.sendall(failure_response)
    finally:
        if 'remote_socket' in locals():
            remote_socket.close()


def handle_http(client_socket, request_data, method, url):
    """ Handles standard HTTP requests. """
    try:
        # Find the Host header to determine the destination server
        headers = request_data.decode('utf-8', 'ignore').split('\r\n')
        host_header = next((h for h in headers if h.lower().startswith('host:')), None)
        
        if not host_header:
            print("[!] Host header not found in request.")
            return

        hostname = host_header.split(' ')[1]
        port = 80 # Default HTTP port

        if ':' in hostname:
            hostname, port_str = hostname.split(':')
            port = int(port_str)

        # Connect to the destination web server
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((hostname, port))
        
        # --- Modify the request header as required ---
        # 1. Change HTTP version to 1.0
        # 2. Force connection to close
        modified_headers = []
        first_line = f"{method} {url} HTTP/1.0"
        modified_headers.append(first_line)
        
        for line in headers[1:]:
            if line.lower().startswith("proxy-connection:"):
                # Replace with 'close'
                modified_headers.append("Proxy-Connection: close")
            elif not line.lower().startswith("connection:"):
                # Keep other headers
                modified_headers.append(line)
        modified_headers.append("Connection: close")

        # The header must end with a double CRLF
        modified_request = "\r\n".join(modified_headers).encode('utf-8') + b'\r\n\r\n'

        remote_socket.sendall(modified_request)
        
        # Start the bidirectional data transfer
        transfer_data(client_socket, remote_socket)

    except socket.error as e:
        print(f"[!] Socket error during HTTP handling: {e}")
    except Exception as e:
        print(f"[!] Error during HTTP handling: {e}")
    finally:
        if 'remote_socket' in locals():
            remote_socket.close()

def transfer_data(sock1, sock2):
    """
    Performs bidirectional data transfer between two sockets using select.
    This is the core of streaming and tunneling.
    """
    sockets = [sock1, sock2]
    while True:
        # Wait for either socket to have data to be read
        readable, _, exceptional = select.select(sockets, [], sockets, 10)
        
        if exceptional:
            print("[!] Exceptional condition on a socket, closing.")
            break
        
        if not readable:
            # Timeout, can happen on idle connections
            continue
            
        for sock in readable:
            try:
                data = sock.recv(BUFFER_SIZE)
                if not data:  # Connection closed by the other end
                    return
                
                # Forward the data to the other socket
                if sock is sock1:
                    sock2.sendall(data)
                else:
                    sock1.sendall(data)
            except socket.error:
                # An error occurred (e.g., connection reset)
                return

if __name__ == '__main__':
    main()