import socket
import threading
import pickle


class Peer:
    s: socket.socket
    peers: list[(str, int)]

    port: int
    manager_port = 1235

    def __init__(self, port_no: int):
        self.port = port_no

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
                self.peers = pickle.loads(msg)
                print(self.peers)
            except ConnectionAbortedError:
                print("connection is closed")
                break


    def __del__(self):
        self.s.close()

    def disconnect(self):
        self.s.close()



if __name__ == "__main__":
    port_no = int(input("Enter Port Number: "))
    p = Peer(port_no)
    p.connect()
    receive_thread = threading.Thread(target=p.receive)
    receive_thread.start()

    while True:
        inp = input(">")
        if inp == 'cls':
            p.disconnect()

        if inp == "conn":
            p = Peer(port_no)
            p.connect()
            receive_thread = threading.Thread(target=p.receive)
            receive_thread.start()




