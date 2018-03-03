#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket

def main():
    # process cli
    args = get_runtime_args()

# start IDS class in 'listen' mode
    ## wait for connection

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

# Retrieve and validate runtime arguments before starting the application
def get_runtime_args():
    try:
        # index 1: port number to open for connections
        if len(sys.argv) == 2:
            return (sys.argv[1])
        else:
            exit_with_msg('Please specify Server input with format:\n`<connection-port>`\n')

    except ValueError:
        exit_with_msg('Port must be an integer. Please try again.')

# Print message then exit
def exit_with_msg(m):
    print ('\nServer Exiting; ' + m)
    exit(0)

if __name__ == '__main__':
    sys.exit(main())
