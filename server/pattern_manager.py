#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import string
import os

PATTERN_FILE = "pattern-config"

def process(args):
    '''
    Process commands entered by user.
    '''

    segs = args.split(' ')
    if not segs:
        print('Please include one of the following commands: add, print, delete, or exit.')
        prompt()

    # define command to execute
    cmd = segs[0].lower()

    # process cmds
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
    '''
    Print contents of pattern-config file.
    '''
    try:
        # create file if doesn't exist
        if not os.path.exists(PATTERN_FILE):
            with open(PATTERN_FILE, 'w'):
                pass
        with open(PATTERN_FILE, 'r') as patterns:
            data = json.load(patterns)
            print('ID\tPattern')
            for entry in data:
                print(entry + '\t' + data[entry])
    except IOError as io_error:
        exit_with_msg('Reading pattern file failed.', io_error)
    except ValueError:
        print('No patterns have been added to the pattern manager yet')

def exec_delete(pattern_id):
    '''
    Delete a pattern from pattern-config using its
    associated id.
    '''

    data = None
    try:
        # create file if it doesn't exist
        if not os.path.exists(PATTERN_FILE):
            with open(PATTERN_FILE, 'w'):
                pass
        # delete pattern and write new contents.
        with open(PATTERN_FILE, 'r') as patterns:
            data = json.load(patterns)
            data.pop(pattern_id)
    except IOError as io_error:
            exit_with_msg('Reading pattern file failed.', io_error)
    except ValueError:
        print('A pattern by that name does not currently exist')
        
    try:
        with open(PATTERN_FILE, 'w') as pattern_json:
            if data:
                json.dump(data, pattern_json)
    except IOError as io_error:
            exit_with_msg('Writing to pattern file failed.', io_error)
    except ValueError:
        print('A pattern by that name does not currently exist')

def exec_add(pattern_id, pattern):
    '''
    Add a new pattern and id to the pattern-config file.
    '''

    # determine if user input is a hex or ascii string
    # if ascii, change to hex
    hex_input = all(c in string.hexdigits for c in pattern)
    if not hex_input:
        pattern = pattern.encode('utf-8').hex()

    # each byte of data -> 2-digit hex representation with hexlify
    # the resulting string is therefore twice as long as number of bytes
    if len(pattern)/2 > 32:
        print('Pattern is more than 32 bytes, please enter another.')
        prompt()

    data = None
    try:
        # create file if does not exist
        if not os.path.exists(PATTERN_FILE):
            with open(PATTERN_FILE, 'w'):
                pass

        # verify that pattern can be added to file
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
        # add pattern to file
        with open(PATTERN_FILE, 'w') as pattern_json:
            if data:
                json.dump(data, pattern_json)
    except IOError as io_error:
            exit_with_msg('Writing to pattern file failed.', io_error)

def exit_with_msg(msg, err):
    '''
    Print message then exit.
    '''
    print ('\nPattern Manager exiting; ' + msg)
    if err:
        print ('\nError recieved: ' + err)
    exit(0)

def print_supported_commands(pre_message):
    '''
    Print supported commands with optional pre-message.
    '''
    if pre_message != None:
        print('\n' + pre_message + '\n')
    print('The supported are as follows:')
    print('`add <pattern_id> <pattern>`: Add a pattern and its id to the pattern-config file.')
    print('`delete <pattern_id>`: Delete a pattern by its id.')
    print('`print`: Print the contents of the pattern-config file.')
    print('`exit`: Exit running application.\n')

def prompt():
    '''
    Prompt user for input.
    '''
    raw_in = input('cmd: ')
    process(raw_in)

def main():
    '''
    Begin user session.
    '''

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
