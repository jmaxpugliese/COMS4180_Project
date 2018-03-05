#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json

PATTERN_FILE = "pattern-config"

def main():
    process()

def process():
    if len(sys.argv) < 2:
        print('Please include one of the following commands: add, print, or delete.')
        sys.exit(0)

    cmd = sys.argv[1]

    # process cmd
    if cmd == 'add':
        if len(sys.argv) < 4:
            print('Add command must be of the following format: add [pattern_id] [pattern]')
            sys.exit(0)
        return exec_add(sys.argv[2], sys.argv[3])

    elif cmd == 'print':
        return exec_print()

    elif cmd == 'delete':
        if len(sys.argv) < 3:
            print('Delete command must be of the following format: delete [pattern_id]')
            sys.exit(0)
        return exec_delete(sys.argv[2])

    else:
        return format_error('Unsupported command.')

def exec_print():
    with open(PATTERN_FILE, 'r') as patterns:
        data = json.load(patterns)
        print('ID\tPattern')
        for entry in data:
            print(entry + '\t' + data[entry])

def exec_delete(pattern_id):
    with open(PATTERN_FILE, 'r') as patterns:
        data = json.load(patterns)
        data.pop(pattern_id)
    with open(PATTERN_FILE, 'w') as pattern_json:
        json.dump(data, pattern_json)

def exec_add(pattern_id, pattern):
    with open(PATTERN_FILE, 'r') as patterns:
        try:
            data = json.load(patterns)
        except ValueError:
            data = {}

        if pattern_id in data:
            print('Pattern id already in use, please choose another.')
            sys.exit(0)
        
        if len(data) == 50:
            print('A maximum of 50 patterns are allowed. Please delete in order to add more.')
            sys.exit(0)

        data[pattern_id] = pattern
   
        with open(PATTERN_FILE, 'w') as pattern_json:
            json.dump(data, pattern_json)

def format_error(error_str):
    return b'0000 ' + str.encode(error_str)

if __name__ == '__main__':
    sys.exit(main())
