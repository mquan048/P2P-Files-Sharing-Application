# creating a manager for Peer to Peer network
import socket
import threading
import time
import pickle


class Manager:
    """
    Manages the network
    """
    s: socket.socket
    connections: dict[(str, int), socket.socket]
    accept_thread: threading.Thread
    broadcast_peers_thread: threading.Thread

    server_ip = ''
    port = 1235
    connections = dict()

    def __init__(self):
        self.s = socket.socket()
        self.s.bind((self.server_ip, self.port))
        self.s.listen(10)
        print("up and running")

    def __del__(self):
        self.s.close()

    def thread_try(addr):
        """
        Trying multi threading
        """
        while True:
            time.sleep(1)
            print(addr)

    def accept_connections(self):
        """
        accepts connections from peers and adds them into a list

        """
        while True:
            c, addr = self.s.accept()
            self.connections[addr] = c
            print(f"Got connection from {addr}")
            self.broadcast_peers_thread = threading.Thread(target=self.broadcast_peers)
            self.broadcast_peers_thread.start()
            self.recv_msg_thread = threading.Thread(target=self.recv_msg)
            self.recv_msg_thread.start()

    def broadcast_peers(self):
        """
        sends the details about peers to other peers
        """
        conn = pickle.dumps(list(self.connections.keys()))
        for addr in self.connections:
            self.connections[addr].send(conn)
        print(self.connections)
        time.sleep(20)

    def run(self):
        self.accept_thread = threading.Thread(target=self.accept_connections)
        self.accept_thread.start()


if __name__ == "__main__":
    manager = Manager()
    manager.run()


