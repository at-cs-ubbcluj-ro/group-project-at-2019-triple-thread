import socket
import cv2
import numpy as np

from main.detector import Detector
from visu.visu import Visu
from threading import Thread
import os
import sys

ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]

PACKET_SIZE = 10000
MIN_PACKETS_ARRIVED = 10
IMAGE_BUFFER_SIZE = 10
saveAllYouGot = False
current_N = 1

if saveAllYouGot:
    file_names = sorted(os.listdir(ROOT_DIR + "/saved"))
    if len(file_names) > 0:
        import re

        for filename in file_names:
            match = re.search('temp(\d+)', filename)
            if match:
                current_N = int(match.group(1))
                current_N += 1

#detector = Detector()
s = socket.socket()
print("Socket successfully created")

# reserve a port for socket connection
port = 12345

# bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
s.bind(('', port))
print("socket binded to %s" % port)

# put the socket into listening mode
s.listen(5)
print("socket is listening")

visu = Visu()
thread = Thread(target=visu.run_visu)
thread.start()


# a forever loop until we interrupt it or
# an error occurs
while True:
    if current_N == IMAGE_BUFFER_SIZE:
        current_N = 1
    print("waiting for clients to connect")
    # Establish connection with client.
    c, addr = s.accept()
    print('Got connection from', addr)

    '''
    size = c.recv(4)
    print("size in 4 bytes hexa:" + str(size))
    size = int.from_bytes(size, "big")
    print("int of size:" + str(size))
    '''

    img_bytes = c.recv(PACKET_SIZE)
    img_bytes2 = c.recv(PACKET_SIZE)
    packets = 2
    while packets < MIN_PACKETS_ARRIVED:
        img_bytes = img_bytes + img_bytes2
        size = len(img_bytes)
        img_bytes2 = c.recv(PACKET_SIZE)
        packets += 1

    img = cv2.imdecode(np.fromstring(img_bytes, dtype='uint8'), 1)
    visu.update_img(img)
    print("saving image from " + str(addr) + " sent through " + str(packets) + " packets")
    if saveAllYouGot:
        # when we are creating datasets we save everything uniquely
        cv2.imwrite(
            ROOT_DIR + "/taken/img" + str(addr[1]) + ".jpeg",
            img)
    else:
        # when we run the application we store only some temporary files, cycling the number
        cv2.imwrite(
            ROOT_DIR + "/taken/img" + str(current_N) + ".jpeg",
            img)
        #UBBdetector.detect(current_img_number=current_N)
        current_N += 1

    # Close the connection with the client
    c.close()
