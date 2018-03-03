#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket

def main():
    # process cli
    args = get_runtime_args()

    # start IDS
    s = init_socket(args)

    # wait for message
    msg = listen(s)

    ## read byte by byte and identifier signature

        ## if sig, drop message & log envent

        ## else, pass message to server

# obtain message
    ## process cmd through IDS

        ### `ls`
            #### return all file names

        ### `get`
            #### load file and send

        ### `put`
            #### save file

        ### send ACK

# listen for messages on initialized port
def listen(s):
    # try:
    # ensure the entire message is received before process
    buff_size = 1024
    msg = b''
    listening = True
    while listening:
        conn, addr = s.accept()
        seg = conn.recv(1024)
        print(seg)
        msg += seg
        if len(seg) < buff_size:
            listening = False
    print (msg)

    conn.send(b'test')
    return msg
    # except:
    #     exit_with_msg('Unable to receive message from client. Please try again.')

# initialize socket for incoming messages
def init_socket(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen(1024)
        print ('IDS is listening on port: %d' % port)
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