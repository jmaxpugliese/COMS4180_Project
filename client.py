#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket

def main():
    # process cli
    args = get_runtime_args()

    # open connection to server
    establish_connection(args[0], args[1])

    # print supported cmd's to user
    print_supported_commands('Welcome to our simple FTP client!')

    # prompt user for input
    prompt()

def establish_connection(ip_addr, socket_no):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((ip_addr, socket_no))
    return s

# prompt user for input
def prompt():
    raw_in = input('cmd: ')
    input_tuple = parse_input(raw_in)
    process_input(input_tuple)

# split input string into command and optional filename tuple
def parse_input(str):
    segs = str.split(' ')
    return (segs[0], (segs[1] if len(segs) > 1 else ''))

# process input
def process_input(input_tuple):
    # process cmd
    if input_tuple[0] == 'put':
        # upload file
        # send
        print('put')

    elif input_tuple[0] == 'get':
        # send cmd
        # save response as file
        print('get')

    elif input_tuple[0] == 'ls':
        # send cmd
        # output response
        print('ls')

    elif input_tuple[0] == 'exit':
        exit_with_msg('Thank you!')

    else:
        print_supported_commands('Unfortunately that command is not supported.')
        prompt()

# Retrieve and validate runtime arguments before starting the application
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

# Print message then exit
def exit_with_msg(m):
    print ('\n\nProgram Exiting; ' + m)
    exit(0)

if __name__ == '__main__':
    sys.exit(main())
