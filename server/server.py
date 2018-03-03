#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def process(msg):
    cmd, filename, payload = parse(msg)

    # process cmd
    if cmd == 'put':
        return exec_put(filename, payload)

    elif cmd == 'get':
        return exec_get(filename)

    elif cmd == 'ls':
        return exec_ls()

    else:
        print(cmd)
        print('sadness')

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
        print(payload)

    return (cmd, filename, payload)

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

def exec_put(filename, payload):
    # try:
        f = open(filename, 'wb')
        f.write(payload)
        f.close()
        return b'Transfer successful'
    # except:
    #     graceful_exit('Error writing to disk.')
