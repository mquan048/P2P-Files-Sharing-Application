from math import ceil
import socket
import threading
import pickle
import os

import logging


PEERS_DIR = './Peers/'
PEER_TIMEOUT = 100


class file:
    chunk_size = 2048
    def __init__(self, filename: str, owner: str):
        self.filename = filename
        self.path = "./Peers/" + owner+"/"+filename


class completeFile(file):

    def __init__(self, filename: str, owner: str):
        super().__init__(filename, owner)
        self.size = self.get_size(self.path)
        self.n_chunks = ceil(self.size/self.chunk_size)
        self.fp = open(self.path, 'rb')

    def get_chunk_no(self, chunk_no):
        return self._get_chunk(chunk_no*self.chunk_size)

    def _get_chunk(self, offset):
        self.fp.seek(offset, 0)
        chunk = self.fp.read(self.chunk_size)
        return chunk

    def get_size(self, path):
        return os.path.getsize(path)

class incompleteFile(file):
    def __init__(self, filename, owner, size):
        super().__init__(filename, owner)
        self.size = size
        self.n_chunks = ceil(self.size/self.chunk_size)
        self.needed_chunks = [i for i in range(self.n_chunks)]
        self.received_chunks = {}
        self.fp = open(self.path, 'wb')

    def get_needed(self):
        self.needed_chunks = []
        for i in range(self.n_chunks):
            if i not in self.received_chunks:
               self.needed_chunks.append(i)
        return self.needed_chunks

    def write_chunk(self, buf, chunk_no):
        self.received_chunks[chunk_no] = buf

    def write_file(self):
        if len(self.get_needed()) == 0:
            with open(self.path, 'wb') as filep:
                for i in range(self.n_chunks):
                    filep.write(self.received_chunks[i])


class Peer:
    s: socket.socket
    peers: list[(str, int)]  # list of all peers
    peers_connections: dict[(str, int), socket.socket]
    port: int
    manager_port = 1233
    addr: (str, int)
    available_files: dict[str, completeFile]


    def __init__(self, port_no: int, name: str, ip_addr='127.0.0.1'):
        self.port = port_no
        self.name = name
        self.directory = PEERS_DIR + name + "/"

        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)

        self.available_files = {}
        for f in os.listdir(self.directory):
            self.available_files[f] = completeFile(f, self.name)

        self.s = socket.socket()

        self.addr = (ip_addr, port_no)
        self.peers_connections = {}
        self.my_socket = socket.socket()
        self.my_socket.bind((ip_addr, self.port))

    def connect_manager(self):
        """
        connect to manager
        """
        self.s.connect(('localhost', self.manager_port))
        msg = self.s.recv(512).decode()
        if msg == 'Send port':
            self.s.send(pickle.dumps(self.addr))

    def receive(self):
        """
        receive the other peers and update the list.
        """
        while True:
            try:
                msg = self.s.recv(512)

                msg = pickle.loads(msg)
                if msg != "testing conn":
                    self.peers = msg['peers']
                    logging.info(f"available peers are {self.peers}")
            except ConnectionAbortedError:
                print("connection with manager is closed")
                break

    def update_peers(self):
        try:
            msg = b"get_peers"
            self.s.send(msg)
        except Exception:
            print("could not get the peers list")

    def __del__(self):
        self.s.close()
        self.my_socket.close()

    def disconnect(self):
        """
        Disconnect the connected socket.
        """
        self.s.send(b"close")
        self.s.close()
        self.my_socket.close()

    def connect_to_peers(self):
        """
        Listens to other peers and adds into peer connections
        """

        self.my_socket.listen(10)
        while True:
            c, addr = self.my_socket.accept()

            self.peers_connections[addr] = {
                "connection": c
            }
            listen_peers_thread = threading.Thread(target=self.listen_to_peer, args=(c, addr))
            listen_peers_thread.start()

    def listen_to_peer(self, c: socket.socket, addr: (str, int)):
        """

        Listen to peer and give response when asked.
        """

        while True:
            try:
                msg = pickle.loads(c.recv(2048))


                if msg['type'] == 'request_file':
                    req_file_name = msg['data']
                    if req_file_name in self.available_files:
                        file_details = pickle.dumps({
                            "type": "available_file",
                            "data": {
                                "filesize": str(self.available_files[req_file_name].size)
                            }
                        })

                        c.send(file_details)

                if msg['type'] == 'request_chunk':
                    file_name = msg['data']['filename']
                    chunk_no = msg['data']['chunk_no']
                    chunk = self.available_files[file_name].get_chunk_no(chunk_no)
                    ret_msg = pickle.dumps({
                        "type": "response_chunk",
                        "data": {
                            "chunk_no": chunk_no,
                            "filename": file_name,
                            "chunk": chunk
                        }
                    })

                    c.send(ret_msg)
            except EOFError: # TODO: don't know what is happening here.
                pass




    def connect_to_peer(self, addr):
        """
        Connect to the peer through new and return the connection.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(addr)
            logging.info(f"Connected to Peer {addr}")
        except:
            print("could not connect to ", addr)
        return sock

    def connect_and_fetch_file_details(self, addr, file_name, file_details: dict[str, object]):
        c = self.connect_to_peer(addr)
        msg = pickle.dumps({
            "type": "request_file",
            "data": file_name
        })
        c.send(msg)
        c.settimeout(PEER_TIMEOUT)
        try:
            msg = pickle.loads(c.recv(512))

            if msg['type'] == "available_file":
                file_details['size'] = msg['data']['filesize']
                file_details['peers_with_file'].append(addr)


        except socket.timeout:
            print("socket did not respond while fetching detail of file")

        c.close()

    def get_peers_with_file(self, file_name: str):
        """
        Check which peers have the file and what parts of it they have.
        Details of the file such as size are also sent.
        """
        running_thread = []
        file_detials = {
            "size": None,
            "peers_with_file": []
        }
        for p in self.peers:
            if p != self.addr:
                get_details_thread = threading.Thread(target=self.connect_and_fetch_file_details,
                                                      args=(p, file_name, file_detials))
                running_thread.append(get_details_thread)
                running_thread[-1].start()

        for threads in running_thread:
            threads.join()

        return file_detials

    def get_chunk_from_peer(self, filename, peer_addr, chunk_no, incomp_file:incompleteFile):
        c = self.connect_to_peer(peer_addr)
        msg = pickle.dumps({
            "type": "request_chunk",
            "data": {
                "filename": filename,
                "chunk_no": chunk_no
            }
        })
        c.send(msg)
        c.settimeout(PEER_TIMEOUT)
        try:
            msg = pickle.loads(c.recv(4096))

            if msg['type'] == "response_chunk":
                incomp_file.write_chunk(msg['data']['chunk'], chunk_no)

        except socket.timeout:
            print(f"peer {peer_addr} did not send the file")

        logging.info(f"received the chunk {chunk_no}")
        c.close()



    def receive_file(self, filename):
        file_details = p.get_peers_with_file(file_name)
        logging.info(f"{file_details}")
        recieving_file = incompleteFile(filename, self.name, int(file_details['size']))

        while len(recieving_file.get_needed()) != 0:
            self.update_peers()
            peers_with_file = self.get_peers_with_file(file_name)['peers_with_file']
            if len(peers_with_file) == 0:
                print(f"there are no peers with file {filename}")
                del recieving_file
                return

            needed_chunks = recieving_file.get_needed()
            i = 0
            running_threads = []
            for peer in peers_with_file:
                if i < len(needed_chunks):
                    get_chunk_thread = threading.Thread(
                        target=self.get_chunk_from_peer,
                        args=(filename, peer, needed_chunks[i], recieving_file)
                    )
                    running_threads.append(get_chunk_thread)
                    get_chunk_thread.start()
                    i += 1
                else:
                    break

            for thread in running_threads:
                thread.join()

        recieving_file.write_file()
        self.available_files[file_name] = completeFile(filename, self.name)
        print(f"recieved {filename}")

def start_peer(port_no, name):
    p = Peer(port_no, name)
    p.connect_manager()
    receive_thread = threading.Thread(target=p.receive)
    receive_thread.start()
    connect_peers_thread = threading.Thread(target=p.connect_to_peers)
    connect_peers_thread.start()

    return p


if __name__ == "__main__":
    port_no = int(input("Enter Port Number: "))
    name = input("Enter your name: ")
    logging.basicConfig(filename="logs/"+name+'.log', encoding='utf-8', level=logging.DEBUG)
    p = start_peer(port_no, name)
    print(f"our available files are: {list(p.available_files.keys())}")
    print("Give one of the commands:")
    print("0|cls: Close the connection with manager")
    print("1|conn: connect to manager")
    print("2|get_peers: update the peers list")
    print("3|get_files: get files from peers\n\n")

    while True:
        inp = input(">")
        if inp == 'cls' or inp == '0':
            p.disconnect()
            del (p)

        if inp == "conn" or inp == '1':
            start_peer(port_no, name)

        if inp == "get_peers" or inp == '2':
            update_peers_thread = threading.Thread(target=p.update_peers)
            update_peers_thread.start()

        if inp == "get_files" or inp == '3':
            file_name = input("Enter file name : ")
            p.receive_file(file_name)
