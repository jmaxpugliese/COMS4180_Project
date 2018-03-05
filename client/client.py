#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import socket

CONNECTED_SOCKET = None

ERROR_MSG_PREFIX = b'0000'

def main():
    # process cli
    args = get_runtime_args()

    # open connection to server
    establish_connection(args[0], args[1])

    # print supported cmd's to user
    print_supported_commands('Welcome to our simple FTP client!')

    # prompt user for input
    while True:
        prompt()

def establish_connection(ip_addr, port):
    try:
        global CONNECTED_SOCKET
        CONNECTED_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CONNECTED_SOCKET.settimeout(10)
        CONNECTED_SOCKET.connect((ip_addr, port))
    except ConnectionRefusedError:
        exit_with_msg('Connection refused. Please check IP Address and port are correct and try again.')

# prompt user for input
def prompt():
    raw_in = input('cmd: ')
    input_tuple = parse_input(raw_in)
    if input_tuple != False:
        process_input(input_tuple)

# split input string into command and optional filename tuple
def parse_input(str):
    segs = str.split(' ')

    # define command to execute
    cmd = segs[0].lower()

    # ensure 2nd argument is optionally defined
    try:
        filename = ''
        if cmd == 'put' or cmd == 'get':
            filename = segs[1]

        if filename.find('/') != -1:
            raise
    except:
        print_error('A <filename> with no path must be provided for this type of command.')
        return False

    return (cmd, filename)

# process input
def process_input(input_tuple):
    # process cmd
    if input_tuple[0] == 'put':
        exec_put(input_tuple[1])

    elif input_tuple[0] == 'get':
        exec_get(input_tuple[1])

    elif input_tuple[0] == 'ls':
        exec_ls()

    elif input_tuple[0] == 'exit':
        CONNECTED_SOCKET.close()
        exit_with_msg('Thank you!')

    else:
        print_supported_commands('Unfortunately that command is not supported.')

# listen for a response on the open socket
def listen():
    try:
        buff_size = 1024
        payload = b''
        listening = True
        while listening:
            seg = CONNECTED_SOCKET.recv(1024)
            payload += seg
            if len(seg) < buff_size:
                listening = False

        if payload[0:4] == ERROR_MSG_PREFIX:
            print_error(payload[5:].decode('utf-8'))
        else:
            return payload
    except socket.timeout:
        print_error('No response from Server. Try again.')

# execute the `ls` command
def exec_ls():
    CONNECTED_SOCKET.send(b'ls')
    response = listen()
    if response != None:
        filelist = response.decode('utf-8')
        print (filelist)

# execute the `get` command
def exec_get(filename):
    try:
        cmd = 'get ' + filename
        CONNECTED_SOCKET.send(str.encode(cmd))
        response = listen()
        if response != None:
            save_received_message(filename, response)
    except:
        print_error('Unable to save ' + filename)

# execute the `put` command
def exec_put(filename):
    try:
        file_bytes = b''
        with open(filename, 'rb') as f:
            byte = f.read(1)
            while byte:
                file_bytes += byte
                byte = f.read(1)

        payload = b'put ' + str.encode(filename) + b' ' + file_bytes
        CONNECTED_SOCKET.send(payload)
        response = listen()
        if response != None:
            print (response)
    except FileNotFoundError:
        print_error(filename + ' does not exist.')
    except:
        print_error('Unable to load ' + filename + '.')

# write message to disk
def save_received_message(filename, text):
    try:
        f = open(filename, 'wb')
        f.write(text)
        f.close()
    except:
        print_error('Error writing to disk.')


# retrieve and validate runtime arguments before starting the application
def get_runtime_args():
    try:
        # index 1: server ip address
        # index 2: server port number to connect
        if len(sys.argv) == 3:
            # validate ip address format
            if sys.argv[1] != 'localhost':
                socket.inet_aton(sys.argv[1])
            # return args as tuple
            return (sys.argv[1], int(sys.argv[2]))
        else:
            exit_with_msg('Please specify Client input with format:\n`<server-ip-address>`\n`<server-connection-port>`\n')

    except OSError:
        exit_with_msg('Invalid IP Address. Please try again')
    except ValueError:
        exit_with_msg('Port must be an integer. Please try again.')

# Print supported commands with optional pre-message
def print_supported_commands(pre_message):
    if pre_message != None:
        print('\n' + pre_message + '\n')
    print('The supported are as follows:')
    print('`put <filename>`: Upload and send <filename> to the server.')
    print('`get <filename>`: Download <filename> from the server.')
    print('`ls`: Print a list of files available to download.')
    print('`exit`: Exit running application.\n')

# Print formatted error message
def print_error(m):
    print('\n\nError: ' + m + '\n')

# Print message then exit
def exit_with_msg(m):
    print ('\n\nProgram Exiting; ' + m)
    exit(0)

if __name__ == '__main__':
    sys.exit(main())
