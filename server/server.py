#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def process(msg):
    cmd, packets = parse(msg)

    # process cmd
    if cmd == 'put':
        # upload file
        # send
        print('put')

    elif cmd == 'get':
        # send cmd
        # save response as file
        print('get')

    elif cmd == 'ls':
        return exec_ls()

    else:
        print('sadness')

# split input string into command and optional filename tuple
def parse(msg):
    segs = msg.split(b' ')
    return (segs[0].decode('utf-8'), (segs[1] if len(segs) > 1 else ''))

def exec_ls():
    files = [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f))]
    response = ' '.join(files)
    return response
