import socket
import threading
import pickle
import os

PEERS_DIR = './Peers/'
PEER_TIMEOUT = 100

class Peer:
    s: socket.socket
    peers: list[(str, int)] # list of all peers
    peers_connections: dict[(str, int), socket.socket]
    port: int
    manager_port = 1233
    addr: (str, int)

    def __init__(self, port_no: int, name: str, ip_addr='127.0.0.1'):
        self.port = port_no
        self.name = name
        self.directory = PEERS_DIR + name + "/"

        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)

        self.available_files = os.listdir(self.directory)
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
                    print(self.peers)
            except ConnectionAbortedError:
                print("connection is closed")
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
            msg = pickle.loads(c.recv(2048))
            print(msg)
            if msg['type'] == 'request_file':
                req_file_name = msg['data']
                if req_file_name in self.available_files:

                    file_list = pickle.dumps({
                      "type": "available_file",
                      "data": {
                          "filesize": str(os.path.getsize(self.directory+req_file_name))
                      }
                    })

                    c.send(file_list)



    def connect_to_peer(self, addr):
        """
        Connect to the peer through new and return the connection.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(addr)
            print(f"Connected to Peer {addr}")
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
            print(msg)
            if msg['type'] == "available_file":
                file_details['size'] = msg['data']['filesize']
                file_details['peers_with_file'].append(addr)
                print("populating file details")

        except socket.timeout:
            print("socket did not respond")
            return

    def get_peers_with_file(self, file_name:str):
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
            if p[1] != self.port: #TODO: store our IP address instead of port
                get_details_thread = threading.Thread(target=self.connect_and_fetch_file_details, args=(p, file_name, file_detials))
                running_thread.append(get_details_thread)
                running_thread[-1].start()
        print(running_thread)
        for threads in running_thread:
            threads.join()
        print(file_detials)


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
    p = start_peer(port_no, name)
    print(f"our available files are: {p.available_files}")
    print("Give one of the commands:")
    print("cls: Close the connection with manager")
    print("conn: connect to manager")
    print("get_peers: update the peers list")
    print("get_files: get files from peers\n\n")

    while True:
        inp = input(">")
        if inp == 'cls':
            p.disconnect()
            del(p)

        if inp == "conn":
            start_peer(port_no, name)

        if inp == "get_peers":
            update_peers_thread = threading.Thread(target=p.update_peers)
            update_peers_thread.start()

        if inp == "get_files":
            file_name = input("Enter file name : ")
            p.get_peers_with_file(file_name)