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

    # wait for message
    msg = listen()

    # send message to server for processing
    response = server.process(msg)

    # respond to client
    send(response)

# listen for messages on initialized port
def listen():
    # try:
    # ensure the entire message is received before process
    buff_size = 1024
    msg = b''
    listening = True
    while listening:
        seg = CONNECTED_SOCKET.recv(1024)
        # inspect segment
        print(seg)
        msg += seg
        if len(seg) < buff_size:
            listening = False

    return msg
    # except:
    #     exit_with_msg('Unable to receive message from client. Please try again.')

def send(r):
    CONNECTED_SOCKET.send(str.encode(r))

    # back to listening
    listen()

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
