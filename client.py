import socket
import threading
import os
from pathlib import Path

def send(socket, message):
    socket.send(message.encode())
    check = socket.recv(BUFSIZE).decode()
    if check != "OK":
        raise Exception('Have error when send message')
        
def receive(socket):
    message = socket.recv(BUFSIZE).decode()
    socket.send("OK".encode())
    return message

def login(server):
    check = False
    while not check:
        username = input('username: ')
        password = input('password: ')
        
        send(server, username)
        send(server, password)
    
        msg = receive(server)
        print(msg)
        
        if msg != 'Login fail':
            check = True

def getListFile(server, uploadServer):
    uploadServerHost, uploadServerPort = uploadServer.getsockname()
    
    send(server, uploadServerHost)
    send(server, str(uploadServerPort))
    
    files = os.listdir(f'{Path(__file__).parent}\\files')
    for file in files:
        send(server, file)
    send(server, "<END>")
    
def initUploadServer():
    peerServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerServer.bind(('127.0.0.1', 0))
    print('Upload server is running on %s:%s' % peerServer.getsockname())
    
    return peerServer
    
def runUploadServer():
    uploadServer.listen(5)
    try: 
        while True:
            peer, peerAddress = uploadServer.accept()
            print('%s:%s has connected.' % peerAddress)
            peerThread = threading.Thread(target=handleUpload, args=(peer,))
            peerThread.start()
             
    finally:
        print('Server close')
        uploadServer.close()

def handleUpload(peer):
    fileName = receive(peer)
    orderUpload = int(receive(peer))
    totalUploader = int(receive(peer))
    
    file = open(f'{Path(__file__).parent}\\files\\{fileName}', 'rb')
    fileSize = os.path.getsize(f'{Path(__file__).parent}\\files\\{fileName}')
    data = file.read()
    
    startRead = (fileSize // totalUploader) * orderUpload
    endRead = fileSize if (fileSize // totalUploader) * (orderUpload + 2) >= fileSize else  (fileSize // totalUploader) * (orderUpload + 1)
     
    dataSend = data[startRead : endRead]
    
    peer.sendall(dataSend)
    peer.send(b'<END>')
    
    print(f"Close connection with {peer.getpeername()}")
    peer.close()

def handleDownload(fileName, listUploadServer, totalUploader):
    listData = [b""] * totalUploader
    listThread = []
    for i in range(0, totalUploader):
        downloadThread = threading.Thread(target=(handleDownloadThread), args=(fileName, i, totalUploader, listUploadServer[i], listData))
        downloadThread.start()
        listThread.append(downloadThread)
        
    for thread in listThread:
        thread.join()
    
    file = open(f'{Path(__file__).parent}\\files\\{fileName}', 'wb')
    
    for data in listData:
        file.write(data)
    
    file.close()

def handleDownloadThread(fileName, orderUpload, totalUploader, uploadAddress, listData):
    uploadServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Connecting to upload server {uploadAddress[0]}:{uploadAddress[1]}')
    uploadServer.connect((uploadAddress[0],int(uploadAddress[1])))

    send(uploadServer, fileName)
    send(uploadServer, str(orderUpload))
    send(uploadServer, str(totalUploader))
    
    fileData = b""
    
    while True:
        data = uploadServer.recv(BUFSIZE)
        fileData += data
        if fileData[-5:] == b"<END>":
            break
        
    listData[orderUpload] = fileData[0:-5]

    print(f"Close connection with {uploadServer.getpeername()}")
    uploadServer.close()
   
HOST = '127.0.0.1'  
PORT = 8000    
BUFSIZE = 1024    
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f'Connecting to server {HOST}:{PORT}')
server.connect((HOST, PORT))

uploadServer = initUploadServer()

if __name__ == '__main__':
    try:
        checkQuit = False
        while not checkQuit:
            login(server)
            uploadServerThread = threading.Thread(target=runUploadServer)
            uploadServerThread.start()
            getListFile(server, uploadServer)
            
            while True: 
                action = input()
                send(server, action)

                if action == 'DOWNLOAD':
                    fileName = input('File need to download: ')
                    send(server, fileName)
                    
                    totalUploader = int(receive(server))
                    listUploadServer = []
                    
                    for i in range(0, totalUploader):
                        uploadServerHost = receive(server)
                        uploadServerPort = receive(server)
                        listUploadServer.append((uploadServerHost, uploadServerPort))
                    
                    downloadThread = threading.Thread(target=handleDownload, args=(fileName, listUploadServer, totalUploader))
                    downloadThread.start()
                    
                elif action == "LOGOUT":
                    msg = receive(server)
                    print(msg)
                    break
                
                elif action == "QUIT":
                    msg = receive(server)
                    print(msg)
                    checkQuit = True
                    break
            
    finally:
        server.close()