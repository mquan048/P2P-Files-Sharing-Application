import socket
import threading

def recvLogin(client, clientAddress):
    account = {}
    username = client.recv(BUFSIZE).decode('utf8')
    client.sendall(bytes(' ', "utf8"))
    password = client.recv(BUFSIZE).decode('utf8')
    account['username'] = username
    account['password'] = password
    return account

def handleUpload(client, clientAddress):
    return

def handleDownload(client, clientAddress):
    return

def handleClient(client, clientAddress):
    global listAccount
    global listAddress
    account = {}
    try:
        while True:
            action = client.recv(BUFSIZE).decode('uft8')
            if action == 'LOGIN' :
                account = recvLogin(client, clientAddress)
                
                #Validation client
                
                listClient.append((account['username'], clientAddress))
                print(listClient)
                
                msg = f"username {account['username']} login successfully"
                client.sendall(msg.encode('utf8'))
                print(msg)
                
            elif action == 'UPLOAD':
                uploadThread = threading.Thread(target=handleClient, args=(client, clientAddress))
                
            elif action == 'DOWNLOAD':
                downloadThread = threading.Thread(target=handleClient, args=(client, clientAddress))
                
            elif action == 'LOGOUT':
                # Remove file of client in listFiles
        
                listClient.remove((account['username'], clientAddress))
                print(listClient)  
            
            elif action == 'QUIT':
                break
            
    finally:
        
        # Remove file of client in listFiles
        
        listClient.remove((account['username'], clientAddress))
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
            clientThread.join()
    finally:
        server.close()