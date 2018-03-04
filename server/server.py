#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def process(msg):
    cmd, filename, file_hash, file_bytes = parse(msg)

    # process cmd
    if cmd == 'put':
        return exec_put(filename, file_hash, file_bytes)

    elif cmd == 'get':
        return exec_get(filename)

    elif cmd == 'ls':
        return exec_ls()

    else:
        return format_error('Unsupported command.')

# split input string into command and optional filename tuple
def parse(msg):
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
    files = [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f))]
    response = ' '.join(files)
    return str.encode(response)

def exec_get(filename):
    # ensure filename is defined
    if len(filename) == 0:
        return format_error('A <filename> must be provided for this type of command.')

    try:
        file_hash = b''
        with open(filename + b'.hash', 'rb') as f:
            byte = f.read(1)
            while byte:
                file_hash += byte
                byte = f.read(1)

        file_bytes = b''
        with open(filename, 'rb') as f:
            byte = f.read(1)
            while byte:
                file_bytes += byte
                byte = f.read(1)
        return file_hash + b' ' + file_bytes
    except FileNotFoundError:
        return format_error(filename.decode('utf-8') + ' does not exist on the server.')
    except:
        return format_error('Server is unable to load ' + filename.decode('utf-8'))

def exec_put(filename, file_hash, file_bytes):
    # ensure filename is defined
    if len(filename) == 0:
        return format_error('A <filename> must be provided for this type of command.')

    # ensure file hash was provided
    if len(file_hash) == 0:
        return format_error('Cannot create a file without a hash.')

    # ensure file contents are defined
    if len(file_bytes) == 0:
        return format_error('Cannot create an empty file.')

    # save hash
    f = open(filename + b'.hash', 'wb')
    f.write(file_hash)
    f.close()

    # save file
    f = open(filename, 'wb')
    f.write(file_bytes)
    f.close()
    return b'Transfer successful'


def format_error(error_str):
    return b'0000 ' + str.encode(error_str)
