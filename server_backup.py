from server import Server
import socket
import threading
import json
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv
from server import Server

load_dotenv()

SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = int(os.getenv('SERVER_PORT'))
BACKUP_HOST = os.getenv('BACKUP_HOST')
BACKUP_PORT = int(os.getenv('BACKUP_PORT'))
BUFFE_SIZE  = int(os.getenv('BUFFE_SIZE'))

class Server_Backup(Server):
    def __init__(self):
        self.addr = (BACKUP_HOST, BACKUP_PORT)
        self.connections = dict[str, tuple[socket.socket, tuple[str, int]]]()
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)
        self.server.listen(10)
        
        print(f"Server backup is running on {self.addr[0]}:{self.addr[1]}")
     
    def run(self):
        self.accept_thread = threading.Thread(target=self.accept_connection)
        self.accept_thread.start()    
        self.server_main_thread = threading.Thread(target=self.conn_server_main_thread)
        self.server_main_thread.start()
    
    def conn_server_main_thread(self):
        try:
            self.server_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_main.connect((SERVER_HOST, SERVER_PORT))
        
            self.server_main.send(pickle.dumps({
                "type": "request",
                "action": "conn_server_main",
            }))
            self.server_main.recv(BUFFE_SIZE)
        
            while True:
                request = pickle.loads(self.server_main.recv(BUFFE_SIZE))
                connections = request["payload"]["connections"]
                for key in connections:
                    self.connections[key] = (None, connections[key])
                self.server_main.send(pickle.dumps({
                    "type": "response",
                    "action": "send_connections",
                    "status": 200,
                }))
        except:
            self.server_main = None
    
    def recv_req(self, client: socket.socket):
        while True:
            try:
                request = pickle.loads(client.recv(BUFFE_SIZE))
                if request["action"] == "login":
                    self.login(request["payload"], client)
                    
                elif request["action"] == "logout":
                    self.logout(request["user"], client)
                
                elif request["action"] == "get_peer_info":
                    self.send_peer_info(request, client)
                
                elif request["action"] == "close_conn":
                    client.close()
                    
                elif request["action"] == "connect_backup":
                    self.connect_backup(request, client)
            except:
                self.handle_suddenly_exit(client)
                print(f"{client.getpeername()[0]}:{client.getpeername()[1]} has disconnected")
                client.close()
                break
            
    def connect_backup(self, request, client):
        if request["user"] is not None:
            self.connections[request["user"]] = (client, request["payload"]["peer_addr"])
        client.send(pickle.dumps({
            "type": "response",
            "action": "connect_backup",
            "status": 200,
            
        }))
        
    def login(self, payload, client: socket.socket):
        username = payload["username"]
        password = payload["password"]
        response = {
            "type": "respone",
            "action": "login",
        }
        
        # check username is logged in
        if username in self.connections:
            response["status"] = 400
            response["payload"] = "The user is already logged in on another device."
            
            client.send(pickle.dumps(response))
            return
         
        with open(f'{Path(__file__).parent}/account.json', 'r') as db:
            account = json.load(db)

        for acc in account:
            if username == acc["username"] and password == acc["password"]:
                self.connections[username] = (client, payload["peer_addr"])
                
                response["status"] = 200
                response["payload"] = f"User {username} log in successfully."
                
                client.send(pickle.dumps(response))
                return
            
        response["status"] = 400
        response["payload"] = "The username or password is incorrect."
              
        client.send(pickle.dumps(response))
       
    def logout(self, username: str, client: socket.socket):
        del self.connections[username]
            
        response = {
            "type": "respone",
            "status": 200,
            "action": "logout",
            "payload": "User log out successfully."
        }
        client.send(pickle.dumps(response))         
             
    def send_peer_info(self, request, client: socket.socket):
        response = {
                "type": "respone",
                "action": "get_peer_info",
            }
        if request["user"] is None or not request["user"] in self.connections:
            response["status"] = 401
            response["payload"] = "The user is not authenticated."
            
        else:
            peer_info = list()
            for conn in self.connections.values():
                peer_info.append(conn[1])
            response["status"] = 200
            response["payload"] = peer_info
            
        client.send(pickle.dumps(response))
        
if __name__ == "__main__":
    try: 
        server = Server_Backup()
        server.run()
        inp = input()
        if inp == "close":
            os._exit(0)

    except KeyboardInterrupt:
        os._exit(0)
        
