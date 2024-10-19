import socket
import threading
import json

def recvLogin(client, clientAddress):
    account = {}
    username = client.recv(BUFSIZE).decode()
    client.send(' '.encode())
    password = client.recv(BUFSIZE).decode()
    
    account[0] = username
    account[1] = password
    
    return account

def validClient(username, password):
    for acc in listClient:
        if acc[0] == username:
            return False
    with open('account.json', 'r') as db:
        accountList = json.load(db)
    for acc in accountList:
        if acc['username'] == username and acc['password'] == str(password):
            return True
    return False

def initUpload(client):
    uploadHost = client.recv(BUFSIZE).decode()
    client.send(' '.encode())
    uploadPort = client.recv(BUFSIZE).decode()
    client.send(' '.encode())
    
    fileName = client.recv(BUFSIZE).decode()
    while fileName != 'END':
        print(fileName)
        listFiles.append((fileName, (uploadHost, uploadPort)))
        client.send(' '.encode())
        fileName = client.recv(BUFSIZE).decode()
    print(listFiles)
    return (uploadHost, uploadPort)

def handleDownload(client):
    fileName = client.recv(BUFSIZE).decode()
    for file in listFiles:
        if file[0] == fileName:
            client.send(file[1][0].encode())
            client.send(file[1][1].encode())
            break

def handleClient(client, clientAddress):
    global listAccount
    global listAddress
    account = {}
    try:
        while True:
            action = client.recv(BUFSIZE).decode()
            print(action)
            if action == 'LOGIN':
                account = recvLogin(client, clientAddress)
                
                #Validation client
                while not validClient(account[0], account[1]):
                    account = {}
                    client.send('Login fail'.encode())
                    account = recvLogin(client, clientAddress)
                
                msg = f"username {account[0]} login successfully"
                client.sendall(msg.encode())
                print(msg) 
                
                peerAddress = initUpload(client) 
                
                listClient.append((account[0], clientAddress, peerAddress))
                print(listClient)          
                
            elif action == 'DOWNLOAD':
                handleDownload(client)
                
            elif action == 'LOGOUT':
                # Remove file of client in listFiles
        
                listClient.remove((account[0], clientAddress))
                print(listClient)  
            
            elif action == 'QUIT':
                break
            
    finally:
        
        # Remove file of client in listFiles
        if account != {}:
            listClient.remove((account[0], clientAddress, peerAddress))
            print(listClient)  
        
        client.close()    
    return

HOST = '127.0.0.1'  
PORT = 8000        
BUFSIZE = 1024

listClient = []
listFiles = []


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

if __name__ == '__main__':
    server.listen(5)
    print(f'Server is running on {HOST}:{PORT}')
    try:
        while True:
            client, clientAddress = server.accept()
            print('%s:%s has connected.' % clientAddress)
            clientThread = threading.Thread(target=handleClient, args=(client, clientAddress))
            clientThread.start()
    finally:
        server.close()