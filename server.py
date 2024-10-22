import socket
import threading
import json
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

def validClient(username, password):
    for acc in listClients:
        if acc[0] == username:
            return False
    with open(f'{Path(__file__).parent}/account.json', 'r') as db:
        accountList = json.load(db)
    for acc in accountList:
        if acc['username'] == username and acc['password'] == str(password):
            return True
    return False

def login(client):
    while True:
        username = receive(client)
        password = receive(client)
        
        if validClient(username, password):
            msg = f"username {username} login successfully"
            send(client, msg)
            print(msg)
            
            return username
        else:
            send(client, "Login fail")  

def logout(account):
    accRemove = None
    for acc in listClients:
        if acc[0] == account:
            accRemove = acc
    for file in listFiles.copy():
        if file[1] == accRemove[2]:
            listFiles.remove(file)
    listClients.remove(accRemove)    
    
def updateListFiles(client):
    uploadHost = receive(client)
    uploadPort = receive(client)
    
    while True:
        fileName = receive(client)
        if fileName == "<END>":
            break
        listFiles.append((fileName, (uploadHost, uploadPort)))
        
    print(listFiles)
    return (uploadHost, uploadPort)

def handleDownload(client):
    fileName = receive(client)
    listPeer = []
    for file in listFiles:
        if file[0] == fileName:
            listPeer.append((file[1][0], file[1][1]))
            
    # send number of peer have this file
    send(client, str(len(listPeer)))
    
    for peer in listPeer:
        send(client, peer[0])
        send(client, peer[1])

def handleClient(client, clientAddress):
    global listAccount
    global listAddress
    try:
        checkQuit = False
        account = None
        while not checkQuit:
            account = login(client)
            uploadAddress = updateListFiles(client)
            listClients.append((account, clientAddress, uploadAddress))
            print(listClients)
            
            while True:
                action = receive(client)
                print(f"{clientAddress[0]}:{clientAddress[1]}: {action}")
                
                if action == "DOWNLOAD":
                    handleDownload(client)
                    
                elif action == "LOGOUT":
                    logout(account)
                    account = None
                    send(client, "Logout successfully")
                    break
                
                elif action == "QUIT":
                    logout(account)
                    account = None
                    send(client, "Logout successfully")
                    checkQuit = True
                    break
    except:
        if not account is None:
            logout(account)
    finally:
        print(f"Close connection with {client.getpeername()}")
        client.close()    

HOST = '127.0.0.1'  
PORT = 8000        
BUFSIZE = 1024

listClients = []
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