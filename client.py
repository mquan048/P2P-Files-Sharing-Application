import socket
import threading
import os

def login(server):
    print('LOGIN')
    server.send('LOGIN'.encode())
    
    check = False
    while not check:
        username = input('username: ')
        password = input('password: ')
        
        server.send(username.encode())
        server.recv(BUFSIZE)
        server.send(password.encode())
    
        msg = server.recv(BUFSIZE).decode()
        print(msg)
        
        if msg != 'Login fail':
            check = True

def getListFile(server, peerServer):
    peerServerHost, peerServerPort = peerServer.getsockname()
    
    server.send(peerServerHost.encode())
    server.recv(BUFSIZE)
    server.send(str(peerServerPort).encode())
    server.recv(BUFSIZE)
    
    files = os.listdir('files')
    for file in files:
        server.send(file.encode())
        server.recv(BUFSIZE)
    server.send('END'.encode())
    
def initPeerServer():
    peerServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerServer.bind(('127.0.0.1', 0))
    print('Upload server is running on %s:%s' % peerServer.getsockname())
    
    return peerServer
    
def runPeerServer():
    peerServer.listen(5)
    try: 
        while True:
            peer, peerAddress = peerServer.accept()
            print('%s:%s has connected.' % peerAddress)
            peerThread = threading.Thread(target=handleUpload, args=(peer, peerAddress))
            peerThread.start()
    finally:
        print('Server close')
        peerServer.close()

def handleUpload(peer, peerAddress):
    fileName = peer.recv(BUFSIZE).decode()
    
    file = open(f'files/{fileName}', 'r')
    fileSize = os.path.getsize(f'files/{fileName}')
    data = file.read()
    
    peer.send(str(fileSize).encode())
    peer.recv(BUFSIZE)
    peer.sendall(data)
    peer.send('END'.encode())
    
    peer.close()

def handleDownload(fileName, peerServerHost, peerServerPort):
    peerServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Connecting to peer server {peerServerHost}:{peerServerPort}')
    peerServer.connect((peerServerHost, int(peerServerPort)))
    
    peerServer.send(fileName.encode())
    
    fileSize = peerServer.recv(BUFSIZE)
    peerServer
    
    fileData = b''
    
    file = open(f'filesDown/{fileName}', 'w')
    
    data = peerServer.recv(fileSize)
    fileData += data
    # while True:
    #     data = peerServer.recv(BUFSIZE)
    #     if data == b"<END>":
    #         break
    #     fileData += data
    file.write(fileData)
    file.close()
    peerServer.close()
   
HOST = '127.0.0.1'  
PORT = 8000    
BUFSIZE = 1024    
peerServer = None
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f'Connecting to server {HOST}:{PORT}')
server.connect((HOST, PORT))

if __name__ == '__main__':
    try:
        while True:
            login(server)
            peerServer = initPeerServer()
            peerServerThread = threading.Thread(target=runPeerServer)
            peerServerThread.start()
            getListFile(server, peerServer)
            
            while True: 
                action = input('Client: ')
                server.send(action.encode())

                if action == 'DOWNLOAD':
                    fileName = input('File need to download: ')
                    server.send(fileName.encode())
                    
                    peerServerHost = server.recv(BUFSIZE)
                    peerServerPort = server.recv(BUFSIZE)
                    
                    downloadThread = threading.Thread(target=handleDownload, args=(fileName, peerServerHost, peerServerPort))
                    downloadThread.start()
                elif action == "LOGOUT":
                    break
    finally:
        server.close()