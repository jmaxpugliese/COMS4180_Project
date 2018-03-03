#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket

def main():
    # process cli
    args = get_runtime_args()

    # print supported cmd's to user
    # print_help()

    # listen for cmd
    cmd = listen()

# process cmd
    ## do `put`
        ### upload file
        ### send

    ## do `get`
        ### send cmd
        ### save response as file

    ## do `ls`
        ### send cmd
        ### output response

    ## do `exit`s

def listen():
    cmd = input('cmd: ')
    return cmd

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
            exit_with_msg('Please specify Client input with format:\n`server-ip-address`\n`server-connection-port`\n')

    except OSError:
        exit_with_msg('Invalid IP Address. Please try again')
    except ValueError:
        exit_with_msg('Port must be an integer. Please try again.')

# Print message then exit
def exit_with_msg(m):
    print ('\n\nProgram Exiting; ' + m)
    exit(0)

if __name__ == '__main__':
    sys.exit(main())
