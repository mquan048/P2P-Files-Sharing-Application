# import socket
# import threading

# def login(server):
#     username = input('username: ')
#     password = input('password: ')

#     server.sendall(bytes(username, 'utf8'))
#     server.recv(BUFSIZE)
#     server.sendall(bytes(password, 'utf8'))

#     msg = server.recv(BUFSIZE).decode
#     print(msg)

#     return

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# print(f'Connecting to server {HOST}:{PORT}')
# server.connect((HOST, PORT))

# if __name__ == '__main__':
#     try:
#         while True:
#             action = input('Client: ')
#             server.sendall(bytes(action, "utf8"))

#             if action == 'LOGIN':
#                 login(server)
#             elif action == "QUIT":
#                 break

#     finally:
#         server.close()

import os
from client_modules.window import initWindow
from client_modules.socket import initSocket
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = os.getenv('SERVER_PORT')
BUFFE_SIZE  = os.getenv('BUFFER_SIZE')
HEIGHT		= os.getenv('HEIGHT')
WIDTH		= os.getenv('WIDTH')
APP_NAME   	= os.getenv('APP_NAME')

if __name__ == '__main__':
    try:
        # Initialize socket connection
        initSocket(SERVER_HOST, SERVER_PORT, BUFFE_SIZE)
    	# Initialize window
        initWindow(APP_NAME, WIDTH, HEIGHT)
    except:
        print("An exception occurred")
    finally:
        print("Program terminated")