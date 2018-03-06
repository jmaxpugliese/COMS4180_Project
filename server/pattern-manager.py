#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import string

PATTERN_FILE = "pattern-config"

def process(args):
    segs = args.split(' ')
    if not segs:
        print('Please include one of the following commands: add, print, delete, or exit.')
        prompt()

    # define command to execute
    cmd = segs[0].lower()

    # process cmd
    if cmd == 'add':
        if len(segs) < 3:
            print('Add command must be of the following format: add [pattern_id] [pattern]')
            prompt()
        exec_add(segs[1], ''.join(segs[2:]))

    elif cmd == 'print':
        exec_print()

    elif cmd == 'delete':
        if len(segs) < 2:
            print('Delete command must be of the following format: delete [pattern_id]')
            prompt()
        exec_delete(segs[1])
    
    elif cmd == 'exit':
        sys.exit(0)

    else:
        print('Unsupported command.')
        prompt()

def exec_print():
    try:
        with open(PATTERN_FILE, 'r') as patterns:
            data = json.load(patterns)
            print('ID\tPattern')
            for entry in data:
                print(entry + '\t' + data[entry])
    except IOError as io_error:
            exit_with_msg('Reading pattern file failed.', io_error)

def exec_delete(pattern_id):
    data = None
    try:
        with open(PATTERN_FILE, 'r') as patterns:
            data = json.load(patterns)
            data.pop(pattern_id)
    except IOError as io_error:
            exit_with_msg('Reading pattern file failed.', io_error)
    try:
        with open(PATTERN_FILE, 'w') as pattern_json:
            if data:
                json.dump(data, pattern_json)
    except IOError as io_error:
            exit_with_msg('Writing to pattern file failed.', io_error)

def exec_add(pattern_id, pattern):
    hex_input = all(c in string.hexdigits for c in pattern)
    if not hex_input:
        pattern = pattern.encode('utf-8').hex()
        
    # Each byte of data -> 2-digit hex representation with hexlify.
    # The resulting string is therefore twice as long as number of bytes.
    if len(pattern)/2 > 32:
        print('Pattern is more than 32 bytes, please enter another.')
        prompt()

    data = None
    try:
        with open(PATTERN_FILE, 'r') as patterns:
            try:
                data = json.load(patterns)
            except ValueError:
                data = {}

            if pattern_id in data:
                print('Pattern id already in use, please choose another.')
                prompt()
            
            if len(data) == 50:
                print('A maximum of 50 patterns are allowed. Please delete in order to add more.')
                prompt()

            data[pattern_id] = pattern

    except IOError as io_error:
            exit_with_msg('Reading pattern file failed.', io_error)
   
    try:
        with open(PATTERN_FILE, 'w') as pattern_json:
            if data:
                json.dump(data, pattern_json)
    except IOError as io_error:
            exit_with_msg('Writing to pattern file failed.', io_error)

# Print message then exit
def exit_with_msg(msg, err):
    print ('\nPattern Manager exiting; ' + msg)
    if err:
        print ('\nError recieved: ' + err)
    exit(0)

# Print supported commands with optional pre-message
def print_supported_commands(pre_message):
    if pre_message != None:
        print('\n' + pre_message + '\n')
    print('The supported are as follows:')
    print('`add <pattern_id> <pattern>`: Add a pattern and its id to the pattern-config file.')
    print('`delete <pattern_id>`: Delete a pattern by its id.')
    print('`print`: Print the contents of the pattern-config file.')
    print('`exit`: Exit running application.\n')

# prompt user for input
def prompt():
    raw_in = input('cmd: ')
    process(raw_in)

def main():
    # print supported cmd's to user
    print_supported_commands('Welcome to our simple Pattern Manager!')

    try:
        # prompt user for input
        while True:
            prompt()

    except KeyboardInterrupt:
        print ('\nPattern Manager exiting.')

if __name__ == '__main__':
    sys.exit(main())
