# creating a manager for Peer to Peer network
import socket
import threading
import time
import pickle

CONN_TEST_TIME = 1


def is_socket_closed(sock: socket.socket) -> bool:
    """
    for a given socket see if it is closed.
    """
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        # sock.settimeout(0.5)
        try:
            obj = pickle.dumps('testing conn')
            sock.send(obj)
        except socket.error:
            return True
        return False

    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        # logger.exception("unexpected exception when checking if a socket is closed")
        return True
    return False


class Manager:
    """
    Manages the network
    """
    s: socket.socket
    connections: dict[(str, int), socket.socket]
    accept_thread: threading.Thread
    broadcast_peers_thread: threading.Thread
    recv_msg_thread: threading.Thread

    server_ip = ''
    port = 1233
    connections = dict()

    def __init__(self):
        self.s = socket.socket()
        self.s.bind((self.server_ip, self.port))
        self.s.listen(10)
        print("up and running")

    def __del__(self):
        self.s.close()

    def accept_connections(self):
        """
        accepts connections from peers and adds them into a list

        """
        while True:
            c, addr = self.s.accept()
            self.connections[addr] = c
            print(f"Got connection from {addr}")

            self.recv_msg_thread = threading.Thread(target=self.recv_msg, args=(c, addr))
            self.recv_msg_thread.start()
            self.start_broadcast_peers_thread()

    def recv_msg(self, c: socket.socket, addr: (str, int)):
        """
        revive msgs from the peers
        """
        while True:
            try:
                msg = c.recv(512).decode()
                if msg == 'close':
                    print(addr)
                    self.connections.pop(addr)
                    self.start_broadcast_peers_thread()
                    break

                if msg == 'get_peers':
                    conn = pickle.dumps({
                        "type": "peers",
                        "peers": list(self.connections.keys())
                    })
                    c.send(conn)
                    break
            except Exception as e:
                print(f"got exception {e} while receiving from addr {addr}")
                break

    def periodic_conn_test(self):
        """
        see if the connected peers are reachable.
        If not, remove them from the peers list and broadcast.
        """
        while True:
            closed_connections = []  # stores the keys for closed connections
            for addr, c in self.connections.items():
                if is_socket_closed(c):
                    closed_connections.append(addr)

            n_closed = len(closed_connections)
            for addr in closed_connections:
                self.connections.pop(addr)

            if n_closed > 0:
                self.start_broadcast_peers_thread()

            time.sleep(CONN_TEST_TIME)

    def start_broadcast_peers_thread(self):
        """
        start the broadcast thread
        """
        self.broadcast_peers_thread = threading.Thread(target=self.broadcast_peers)
        self.broadcast_peers_thread.start()

    def broadcast_peers(self):
        """
        sends the details about peers to other peers
        """
        conn = pickle.dumps({
            "type": "peers",
            "peers": list(self.connections.keys())
        })
        for addr in self.connections:
            self.connections[addr].send(conn)

    def run(self):
        """
        run the manager
        """
        self.accept_thread = threading.Thread(target=self.accept_connections)
        self.accept_thread.start()
        self.periodic_conn_test_thread = threading.Thread(target=self.periodic_conn_test)
        self.periodic_conn_test_thread.start()


if __name__ == "__main__":
    manager = Manager()
    manager.run()
