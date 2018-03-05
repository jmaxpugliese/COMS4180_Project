#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket
import json
import binascii
import server
import datetime

CONNECTED_SOCKET = None
CONNECTED_CLIENT = None
PACKET_SIZE = 1024
PATTERN_FILE = "pattern-config"
LOG_FILE = "ids-log"

def main():
    # process cli
    args = get_runtime_args()

    # start IDS
    s = init_socket(args)

    run()


def run():
    while True:
        # wait for message
        msg = listen()

        # send message to server for processing
        byte_response = server.process(msg)

        # respond to client
        send(byte_response)

def check_packet(pkt):
    hex_pkt = str(binascii.hexlify(pkt))
    with open(PATTERN_FILE, 'r') as patterns:
        data = json.load(patterns)
        for entry in data:
            if data[entry] in hex_pkt:
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write('Pattern ID: ' + entry + '; Client IP: ' + CONNECTED_CLIENT[0] + '; Timestamp: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n')
                return False
    return True


# listen for messages on initialized port
def listen():
    try:
        # ensure the entire message is received before process
        buff_size = 1024
        msg = b''
        listening = True
        while listening:
            seg = CONNECTED_SOCKET.recv(1024)
            process_pkt = check_packet(seg)
            # inspect segment

            if process_pkt:
                msg += seg

            if len(seg) < buff_size:
                listening = False

        return msg
    except ConnectionResetError:
        CONNECTED_SOCKET.close()
        exit_with_msg('Socket connection reset. Please start application again.')
    except:
        exit_with_msg('Unable to receive message from client. Please try again.')

def send(b):
    try:
        print(b)
        CONNECTED_SOCKET.send(b)
    except:
        CONNECTED_SOCKET.close()
        exit_with_msg('Unknown error; exiting IDS.')

# initialize socket for incoming messages
def init_socket(port):
    try:
        global CONNECTED_SOCKET
        global CONNECTED_CLIENT
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (socket.gethostbyname(socket.gethostname()), port)
        print('Starting up on ip {} port {}'.format(server_address[0], server_address[1]))
        s.bind(server_address)
        #s.bind(('', port))
        s.listen(1024)
        print ('IDS is listening on port: %d' % port)
        CONNECTED_SOCKET, CONNECTED_CLIENT = s.accept()
        return s
    except:
        exit_with_msg('Unable to bind to port and listen for messages. Please try again.')

# Retrieve and validate runtime arguments before starting the application
def get_runtime_args():
    try:
        # index 1: port number to open for connections
        if len(sys.argv) == 2:
            return (int(sys.argv[1]))
        else:
            exit_with_msg('Please specify input with format:\n`<connection-port>`\n')

    except ValueError:
        exit_with_msg('Port must be an integer. Please try again.')

# Print message then exit
def exit_with_msg(m):
    print ('\nIDS & Server Exiting; ' + m)
    exit(0)

if __name__ == '__main__':
    sys.exit(main())
