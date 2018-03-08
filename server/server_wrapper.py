#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import server
import ids

'''
Wrapper for ids and server functions. Parses user input, initializes the ids,
and relays communication between the ids and server.
'''

def get_runtime_args():
    '''
    Retrieve and validate runtime arguments before starting the application.
    '''

    if len(sys.argv) != 2:
        print('Please specify input with format:\n`<connection-port>`\n')
        exit(0)

    if not sys.argv[1].isdigit():
        print('Port must be an integer. Please try again.')
        exit(0)

    port = int(sys.argv[1])
    if port < 0 or port > 65535:
        print('Port number must be betwen 0-65535.')
        exit(0)

    return port

def server_ids_relay(msg):
    '''
    Ids calls this function which in turn sends the client data to
    the server and sends the server's response to the ids.
    '''
    return server.process(msg)

def main():
    '''
    Starts ids with port from commandline arguments.
    '''

    port = get_runtime_args()
    ids_obj = ids.Ids(port)
    ids_obj.run()

if __name__ == '__main__':
    main()
