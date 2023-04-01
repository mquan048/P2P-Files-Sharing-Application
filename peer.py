import socket
import threading
import pickle
import os

PEERS_DIR = './Peers/'


class Peer:
    s: socket.socket
    peers: list[(str, int)]

    port: int
    manager_port = 1233

    def __init__(self, port_no: int, name: str):
        self.port = port_no
        self.name = name
        self.directory = PEERS_DIR + name + "/"

        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)

        self.available_files = os.listdir(self.directory)
        self.s = socket.socket()

    def connect(self):
        """
        connect to manager
        """
        self.s.bind(('', self.port))
        self.s.connect(('localhost', self.manager_port))

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

    def disconnect(self):
        """
        Disconnect the connected socket.
        """
        self.s.send(b"close")
        self.s.close()


if __name__ == "__main__":
    port_no = int(input("Enter Port Number: "))
    name = input("Enter your name: ")

    p = Peer(port_no, name)
    p.connect()
    receive_thread = threading.Thread(target=p.receive)
    receive_thread.start()
    print(p.available_files)

    while True:
        inp = input(">")
        if inp == 'cls':
            p.disconnect()


        if inp == "conn":
            p = Peer(port_no, name)
            p.connect()
            receive_thread = threading.Thread(target=p.receive)
            receive_thread.start()

        if inp == "get_peers":
            update_peers_thread = threading.Thread(target=p.update_peers)
            update_peers_thread.start()