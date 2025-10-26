"""
Main module for the proxy server
"""
import SocketManager

def main():
    try:
        proxy_socket_manager = SocketManager()
        proxy_socket_manager.start()
        proxy_socket_manager.run()
    except Exception as e:
        print(f"Error in setting up proxy server : {e}")

if __name__ == '__main__':
    main()