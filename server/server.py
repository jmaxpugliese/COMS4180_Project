#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

'''
Server functions that process commands from the client, with no actual connection to the client.
The server processes client data from the ids that is sent through server_wrapper. Once processed,
the server will send its response to the ids through server_wrapper.
'''

ERROR_MSG_PREFIX = b'0000'
SUCCESS_MSG_PREFIX = b'1111'
FILE_DIR = './files'

def process(msg):
    '''
    Process client requests.
    '''

    # this case occurs when the entire client request is dropped
    # ids adds '\n' to close a file in case last packet is dropped
    if msg == b'\n':
        return format_error('Unable to process request.')
    
    cmd, filename, file_hash, file_bytes = parse(msg)

    # process cmd
    if cmd == 'put':
        return exec_put(filename, file_hash, file_bytes)

    elif cmd == 'get':
        print(file_hash)
        return exec_get(filename)

    elif cmd == 'ls':
        return exec_ls()

    # nothing to process
    # send ids signal to close connection
    elif cmd == 'exit':
        return None

    return format_error('Unsupported command.')

def parse(msg):
    '''
    Split input string into command and optional filename tuple.
    '''

    segs = msg.split(b' ')

    # parse cmd
    cmd = segs[0].decode('utf-8').lower()

    # optionally, parse filename
    filename = ''
    if len(segs) > 1:
        filename = segs[1]

    # optionally, parse file hash
    file_hash = b''
    if len(segs) > 2:
        file_hash = segs[2]
        print(file_hash)

    # optionally, parse file contents
    file_bytes = b''
    if len(segs) > 3:
        file_bytes = b' '.join(segs[3:])

    return (cmd, filename, file_hash, file_bytes)

def exec_ls():
    '''
    Execute the `ls` command.
    '''

    # add all files in the ./files directory
    files = [f for f in os.listdir(FILE_DIR) if os.path.isfile(os.path.join(FILE_DIR, f))]
    response = ' '.join(files)
    return SUCCESS_MSG_PREFIX + str.encode(response)

def exec_get(filename):
    '''
    Execute the `get` command.
    '''

    # ensure filename is defined
    if not filename:
        return format_error('A <filename> must be provided for this type of command.')

    try:
        # retrieve and send file contents.
        file_hash = b''
        hash_path = os.path.join(FILE_DIR, filename.decode('utf-8') + b'.hash')
        with open(hash_path, 'rb') as f:
            hash_bytes = bytes(f.read())

        file_bytes = b''
        file_path = os.path.join(FILE_DIR, filename.decode('utf-8'))
        with open(file_path, 'rb') as f:
            file_bytes = bytes(f.read())
        return SUCCESS_MSG_PREFIX + file_hash + b' ' + file_bytes
    except FileNotFoundError:
        return format_error(filename.decode('utf-8') + ' does not exist on the server.')
    except IOError:
        return format_error('Server is unable to read ' + filename.decode('utf-8'))

def exec_put(filename, file_hash, file_bytes):
    '''
    Execute the `put` command.
    '''

    # ensure filename is defined
    if not filename:
        return format_error('A <filename> must be provided for this type of command.')

    # ensure file hash was provided
    if not file_hash:
        return format_error('Cannot create a file without a hash.')

    # ensure payload is defined
    if not file_bytes:
        return format_error('Cannot create an empty file.')
    try:
         # write hash contents to ./files directory
        hash_path = os.path.join(FILE_DIR, filename.decode('utf-8') + b'.hash')
        with open(hash_path, 'wb') as f:
            f.write(file_hash)

        # write file contents to ./files directory
        file_path = os.path.join(FILE_DIR, filename.decode('utf-8'))
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
    except IOError:
            format_error('Writing to file ' + filename.decode('utf-8') + ' failed.')
    return SUCCESS_MSG_PREFIX + b'Transfer successful'


def format_error(error_str):
    '''
    Add error code to server response.
    '''

    return ERROR_MSG_PREFIX + str.encode(error_str)
