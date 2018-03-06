#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

ERROR_MSG_PREFIX = b'0000 '

def process(msg):
    if msg == b'':
        return format_error('Unable to process request.')
    
    cmd, filename, payload = parse(msg)

    # process cmd
    if cmd == 'put':
        return exec_put(filename, payload)

    elif cmd == 'get':
        return exec_get(filename)

    elif cmd == 'ls':
        return exec_ls()

    elif cmd == 'exit':
        return None

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

    # optionally, parse file payload
    payload = ''
    if len(segs) > 2:
        payload = b' '.join(segs[2:])

    return (cmd, filename, payload)

def exec_ls():
    files = [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f))]
    response = ' '.join(files)
    return str.encode(response)

def exec_get(filename):
    # ensure filename is defined
    if not filename:
        return format_error('A <filename> must be provided for this type of command.')

    try:
        file_bytes = b''
        with open(filename, 'rb') as f:
            file_bytes = bytes(f.read())
        return file_bytes
    except FileNotFoundError:
        return format_error(filename.decode('utf-8') + ' does not exist on the server.')
    except IOError:
        return format_error('Server is unable to read ' + filename.decode('utf-8'))

def exec_put(filename, payload):
    # ensure filename is defined
    if not filename:
        return format_error('A <filename> must be provided for this type of command.')

    # ensure payload is defined
    if not payload:
        return format_error('Cannot create an empty file.')
    try:
        with open(filename, 'wb') as f:
            f.write(payload)
    except IOError:
            format_error('Writing to file ' + filename.decode('utf-8') + ' failed.')
    return b'Transfer successful'
    # except:
    #     graceful_exit('Error writing to disk.')

def format_error(error_str):
    return ERROR_MSG_PREFIX + str.encode(error_str)
