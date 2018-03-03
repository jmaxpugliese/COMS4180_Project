#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def process(msg):
    cmd, payload = parse(msg)

    # process cmd
    if cmd == 'put':
        # upload file
        # send
        print('put')

    elif cmd == 'get':
        return exec_get(payload)

    elif cmd == 'ls':
        return exec_ls()

    else:
        print(cmd)
        print('sadness')

# split input string into command and optional filename tuple
def parse(msg):
    segs = msg.split(b' ')
    return (segs[0].decode('utf-8').lower(), (segs[1] if len(segs) > 1 else ''))

def exec_ls():
    files = [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f))]
    response = ' '.join(files)
    return str.encode(response)

def exec_get(filename):
    try:
        file_bytes = b''
        with open(filename, 'rb') as f:
            byte = f.read(1)
            while byte:
                file_bytes += byte
                byte = f.read(1)
        return file_bytes
    except:
        graceful_exit('Error loading transfer file. Please try again.')
