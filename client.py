import socket
import threading

def login(server):
    username = input('username: ')
    password = input('password: ')
    
    server.sendall(bytes(username, 'utf8'))
    server.recv(BUFSIZE)
    server.sendall(bytes(password, 'utf8'))
    
    msg = server.recv(BUFSIZE).decode
    print(msg)
    
    return

HOST = '127.0.0.1'  
PORT = 8000    
BUFSIZE = 1024    

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f'Connecting to server {HOST}:{PORT}')
server.connect((HOST, PORT))

if __name__ == '__main__':
    try:
        while True:
            action = input('Client: ')
            server.sendall(bytes(action, "utf8"))

            if action == 'LOGIN':
                login(server)
            elif action == "QUIT":
                break
            
    finally:
        server.close()