#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket

import server

CONNECTED_SOCKET = None

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
    print(pkt)
# listen for messages on initialized port
def listen():
    try:
        # ensure the entire message is received before process
        buff_size = 1024
        msg = b''
        listening = True
        while listening:
            seg = CONNECTED_SOCKET.recv(1024)
            check_packet(seg)
            # inspect segment
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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen(1024)
        print ('IDS is listening on port: %d' % port)
        CONNECTED_SOCKET, addr = s.accept()
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
