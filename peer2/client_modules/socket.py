import socket
import threading
import os
import pickle
import tqdm
from pathlib import Path
from math import ceil

CHUNK_SIZE = 512

class Server:
    server: socket.socket
    list_peers_addr: list[(str, int)]
    peer_addr: tuple[str, int]
    user = None
    
    def __init__(self, SERVER_HOST, SERVER_PORT, BACKUP_HOST, BACKUP_PORT, BUFFE_SIZE):
        self.server_addr = (SERVER_HOST, SERVER_PORT)
        self.server_backup_addr = (BACKUP_HOST, BACKUP_PORT)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.BUFFE_SIZE = BUFFE_SIZE
        
        self.list_peers_addr = list[tuple[str, int]]()
        
        
    def __del__(self):
        self.server.close()
        
    def run(self, peer):
        try:
            self.peer_addr = peer.peer.getsockname()
        
            self.server.connect(self.server_addr)
            print(f'Connecting to server {self.server_addr[0]}:{self.server_addr[1]}')
        except:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect(self.server_backup_addr)
            print(f'Connecting to server backup {self.server_backup_addr[0]}:{self.server_backup_addr[1]}')
    
    def reconnect_server_backup(self, request):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect(self.server_backup_addr)
            print(f'Connecting to server backup {self.server_backup_addr[0]}:{self.server_backup_addr[1]}')
            # Send info user to server backup
            self.server.send(pickle.dumps({
                "type": "request",
                "action": "connect_backup",
                "user": self.user,
                "payload": {
                    "peer_addr": self.peer_addr
                },
            }))
            self.server.recv(self.BUFFE_SIZE)
            # Send the request again
            self.server.send(pickle.dumps(request))
            response = pickle.loads(self.server.recv(self.BUFFE_SIZE))
            
            return response
            
        except:
            print("Server and server backup are not available")
            os._exit(0)
        
    def login(self, username, password):
        request = {
            "type": "request",
            "action": "login",
            "payload": {
                "username": username,
                "password": password,
                "peer_addr": self.peer_addr,
            },
        }
        try:
            self.server.send(pickle.dumps(request))
            response = pickle.loads(self.server.recv(self.BUFFE_SIZE))
        except:
            response = self.reconnect_server_backup(request)
        print(response["payload"])
        if response["status"] == 200:
            self.user = username
            return True, response["payload"]
        else:
            return False, response["payload"]

    def logout(self):
        request = {
            "type": "request",
            "user": self.user,
            "action": "logout",
        }
        try:
            self.server.send(pickle.dumps(request))
            response = pickle.loads(self.server.recv(self.BUFFE_SIZE))
        except:
            response = self.reconnect_server_backup(request)
        print(response["payload"])
        
        self.user = None
    
    def get_peer_info(self):
        request = {
            "type": "request",
            "user": self.user,
            "action": "get_peer_info",
        }   
        try:
            self.server.send(pickle.dumps(request))
            response = pickle.loads(self.server.recv(self.BUFFE_SIZE))
        except:
            response = self.reconnect_server_backup(request)
        if response["status"] == 401:
            print(response["payload"])
            
        else:
            self.list_peers_addr = response["payload"]
    
class Peer:
    peer: socket.socket
    available_files: dict[(str, int), set[(str, int)]] # dict[(filename, size), set[peer_addr]]
    server: Server
    
    def __init__(self, server: Server, BUFFE_SIZE, LOCAL_DIR, SHARE_DIR):
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer.bind(('127.0.0.1', 0))
        
        self.BUFFE_SIZE = BUFFE_SIZE
        self.local_dir = LOCAL_DIR
        self.share_dir = SHARE_DIR
        
        self.available_files = dict[tuple[str, int], set[tuple[str, int]]]()
        self.server = server
        
    def __del__(self):
        self.peer.close()
    
    def run(self):
        self.peer.listen(10)
        self.accept_thread = threading.Thread(target=self.accept_connection)
        self.accept_thread.start()

    def accept_connection(self):
        while True:
            peer, peer_addr = self.peer.accept()
            peer_thread = threading.Thread(target=self.listen_peer, args=(peer,))
            peer_thread.start()
            
    def listen_peer(self, peer: socket.socket):
        while True:
            resquest = pickle.loads(peer.recv(self.BUFFE_SIZE))
            if resquest["action"] == "fetch_file":
                payload = resquest["payload"]
                
                file = Read_File(payload["filename"], payload["size"], self.share_dir)
                data = file.read(payload["chunk_no"])
                
                response = {
                    "type": "response",
                    "status": 200,
                    "action": "fetch_file",
                    "payload": {
                        "filename": payload["filename"],
                        "size": payload["size"],
                        "chunk_no": payload["chunk_no"],
                        "data": data
                    },
                }
                peer.send(pickle.dumps(response))
                
                del file
            
            elif resquest["action"] == "get_shared_file":
                list_files_res = list[tuple[str, int]]()
                
                path_folder = Path.joinpath(Path(__file__).parents[1], self.share_dir)
                files = os.listdir(path_folder)
                for file in files:
                    fileSize = os.path.getsize(Path.joinpath(path_folder, file))
                    list_files_res.append((file, fileSize))
                    
                response = {
                    "type": "response",
                    "status": 200,
                    "action": "get_shared_file",
                    "payload": list_files_res,
                }
                peer.send(pickle.dumps(response))
                
                
            elif resquest["action"] == "close_conn":
                peer.close()
                break

    def get_available_files(self):
        self.server.get_peer_info()
        running_thread = list[threading.Thread]()
        new_available_files = dict[tuple[str, int], set[tuple[str, int]]]()
        
        for peer_addr in self.server.list_peers_addr:
            if peer_addr == self.peer.getsockname():
                continue
            
            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer.connect(peer_addr)
            
            peer_thread = threading.Thread(target=self.get_shared_file, args=(peer, new_available_files))
            peer_thread.start()
            running_thread.append(peer_thread)
            
        for thread in running_thread:
            thread.join()
            
        self.available_files = new_available_files
            
    def get_shared_file(self, peer: socket.socket, new_available_files: dict[tuple[str, int], set[tuple[str, int]]]):
        resquest = {
            "type": "request",
            "action": "get_shared_file",
        }
        peer.send(pickle.dumps(resquest))
        response = pickle.loads(peer.recv(self.BUFFE_SIZE))
        for file in response["payload"]:
            if file in new_available_files:
                new_available_files[file].add(peer.getpeername())
            else:
                new_available_files[file] = set([peer.getpeername()])
                
        peer.send(pickle.dumps({
            "type": "request",
            "action": "close_conn",
        }))
        peer.close()

class Read_File:
    filename: str
    size: int
    path_folder: str
    
    chunk_size = CHUNK_SIZE
    
    def __init__(self, filename, size, share_dir):
        self.filename = filename
        self.size = size
        self.share_dir = share_dir
        self.path_folder = Path.joinpath(Path(__file__).parents[1], self.share_dir)
        
    def read(self, chunk_no):
        file = open(Path.joinpath(self.path_folder, self.filename), "rb")
        file.seek(chunk_no * self.chunk_size, 0)
        data = file.read(self.chunk_size)
        return data
           
class Fetch_File:
    filename: str
    size: int
    path_folder: str
    
    total_chunk: int
    current_chunk: int
    chunk_data: list[str]
    
    peers: list[socket.socket]
    
    chunk_size = CHUNK_SIZE
        
    def __init__(self, filename, size, available_files, BUFFE_SIZE, local_dir):
        self.BUFFE_SIZE = BUFFE_SIZE
        
        self.filename = filename
        self.size = size
        self.local_dir = local_dir
        self.path_folder = Path.joinpath(Path(__file__).parents[1], self.local_dir)
        
        self.init_chunk()
        
        self.peers = list[socket.socket]()
        
        if (filename, size) in available_files:
            peers_addr = available_files[(filename, size)]
        else:
            peers_addr = set[tuple[str, int]]()
            
        for peer_addr in peers_addr:
            p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            p.connect(peer_addr)
            self.peers.append(p)
        
    def __del__(self):
        for peer in self.peers:
            peer.close()
    
    def init_chunk(self):
        self.total_chunk = ceil(self.size / self.chunk_size)
        self.current_chunk = 0
        self.chunk_data = [b""] * self.total_chunk
        
        self.is_access_cur_chunk = False
        
    def get_chunk_no(self) -> int:
    # Handling the race condition of variable current_chunk.
        while self.is_access_cur_chunk:
            pass
        
        self.is_access_cur_chunk = True
        
        chunk_no = self.current_chunk
        if self.current_chunk < self.total_chunk:
            self.current_chunk += 1
        
        self.is_access_cur_chunk = False
            
        return chunk_no
    
    def fetch_file(self):
        if not self.peers:
            return "File not found."
        
        running_thread = list[threading.Thread]()
        progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=self.size, desc=self.filename)
        
        for peer in self.peers:
            fetch_thread = threading.Thread(target=self.fetch_chunk, args=(peer, progress,))
            fetch_thread.start()
            running_thread.append(fetch_thread)
            
        for fetch_thread in running_thread:
            fetch_thread.join()
            
        file = open(Path.joinpath(self.path_folder, self.filename), "wb")
        
        for data in self.chunk_data:
            file.write(data)
            
        file.close()
        
        return f"Fetch file {self.filename} successfully."
    
    def fetch_chunk(self, peer: socket.socket, progress: tqdm.tqdm):
        while True:
            chunk_no = self.get_chunk_no()
            
            if chunk_no < self.total_chunk:
                resquest = {
                    "type": "request",
                    "action": "fetch_file",
                    "payload": {
                        "filename": self.filename,
                        "size": self.size,
                        "chunk_no": chunk_no
                    },
                }
                peer.send(pickle.dumps(resquest))
                
                response = pickle.loads(peer.recv(self.BUFFE_SIZE))
                
                data = response["payload"]["data"]
                self.chunk_data[chunk_no] = data
                
                progress.update(self.chunk_size)
                
            else:
                resquest = {
                    "type": "request",
                    "action": "close_conn",
                }
                peer.send(pickle.dumps(resquest))
                peer.close()
                break                           

def initSocket(SERVER_HOST, SERVER_PORT, BACKUP_HOST, BACKUP_PORT, BUFFE_SIZE, LOCAL_DIR, SHARE_DIR):
    server = Server(SERVER_HOST, SERVER_PORT, BACKUP_HOST, BACKUP_PORT, BUFFE_SIZE)
    peer = Peer(server, BUFFE_SIZE, LOCAL_DIR, SHARE_DIR) 
    server.run(peer)
    peer.run()
    
    return server, peer
    # print(f'Connecting to server {SERVER_HOST}:{SERVER_PORT} with buffer size {BUFFE_SIZE}')
