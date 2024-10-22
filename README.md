# P2P file transfer

Please Look at the video demo here.
https://youtu.be/f5CXSABgg7g

This repository contains the crude implementation of the peer to peer
protocol. 

There is
* manager
* peer

The manager has the data of all the peers that are in the network. When
a new peer joins the network he pings the manager and gets the list 
of all active peers in the network.

When a peer needs a file, he/she asks other peers whether they have the
file. If Multiple peers have the file, chunks of the files are received from 
each of the peers. After receiving the whole file, peer reassembles 
the file and saves it.

## To run the file
1. `python Manager.py`
2. `python Peer.py`

Run running peer, it will ask you to select a _**port**_ and **_name_**.

name should be same as the name of the folder inside the `Peers` folder

 As new peers join, or peers leave, the manager broadcasts a list 
 of active peers. The list is written in `logs/<name>.log` file for
 convenience.

From one of the peers, select the `3`rd option ie, `get_files`. Then you can 
request which file you want.
If the file exists it will be transferred from other peers and will be stored
in the `./Peers/<name>/` folder.

Currently, the peer folder contains `a`. The peer `a` contains a example.txt.
Thus we can run `a` as one of the peer, other peer as let's say `b`. Now, from peer `b` 
we can ask for file `example.txt`. 
The file will be transferred to `a`. 


 
