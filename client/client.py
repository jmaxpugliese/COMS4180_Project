#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import hashlib

ERROR_MSG_PREFIX = b'0000'
SUCCESS_MSG_PREFIX = b'1111'

class Client(object):
    '''
    Client class takes as input a server IP address and port number.
    The client will either (a) put: send a file to the server,
    (b) get: request and receive a file from the server, (c) ls: request
    and recieve a list of files on the server, or (d) exit: exit the session.
    The client connects to the server and sends data based on the chosen action.
    '''

    # all files client can access will be in this folder
    FILE_DIR = './files'

    def __init__(self):
        self._sock = None
        self._port = None
        self._ip_addr = None

        # initialize class members with command line arguments
        try:
            # index 1: server ip address
            # index 2: server port number to connect
            if len(sys.argv) == 3:
                self._port = int(sys.argv[2])
                if self._port < 0 or self._port > 65535:
                    self.exit_with_msg('Port number must be betwen 0-65535.', None)
                
                # validate ip address format
                if sys.argv[1] != 'localhost':
                    socket.inet_aton(sys.argv[1])

                self._ip_addr = sys.argv[1]
            else:
                self.exit_with_msg('Please specify Client input with format:\n`<server-ip-address>`\n`<server-connection-port>`\n', None)

        except OSError:
            self.exit_with_msg('Invalid IP Address. Please try again', None)
        
        except ValueError:
            self.exit_with_msg('Port must be an integer. Please try again.', None)

    def establish_connection(self):
        '''
        Establish connection with server.
        '''
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(10)
            self._sock.connect((self._ip_addr, self._port))

        except ConnectionRefusedError:
            self.exit_with_msg('Connection refused. Please check IP Address and port are correct and try again.', None)
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)

    def prompt(self):
        '''
        Prompt user for input.
        '''
        raw_in = input('cmd: ')
        input_tuple = self.parse_input(raw_in)
        if input_tuple != False:
            self.process_input(input_tuple)

    def parse_input(self, args):
        '''
        Split input string into command and optional filename tuple.
        '''
        segs = args.split(' ')

        # define command to execute
        cmd = segs[0].lower()

        # ensure 2nd argument is optionally defined
        filename = ''
        if cmd == 'put' or cmd == 'get':
            filename = segs[1]

        # all files are assumed to be in ./files
        if filename.find('/') != -1:
            self.print_error('A <filename> with no path must be provided for this type of command.')
            return False

        return (cmd, filename)

    def process_input(self, input_tuple):
        '''
        Process commands.
        '''

        if input_tuple[0] == 'put':
            self.exec_put(input_tuple[1])

        elif input_tuple[0] == 'get':
            self.exec_get(input_tuple[1])

        elif input_tuple[0] == 'ls':
            self.exec_ls()

        elif input_tuple[0] == 'exit':
            self.exec_exit()

        else:
            self.print_supported_commands('Unfortunately that command is not supported.')

    def listen(self):
        '''
        Listen for a response from the server on the open socket.
        '''
        try:
            buff_size = 4096
            payload = b''
            listening = True
            self._sock.settimeout(60)
            while listening:
                seg = self._sock.recv(buff_size)
                payload += seg
                if len(seg) < buff_size:
                    listening = False

            # check if response is an error or not
            if payload[0:4] == ERROR_MSG_PREFIX:
                self.print_error(payload[4:].decode('utf-8'))
            
            # check that response has success code
            elif payload[0:4] == SUCCESS_MSG_PREFIX:
                return payload[4:]
            # else:
            #     return payload
        except socket.timeout:
            self.print_error('No response from Server. Try again.')

    def exec_ls(self):
        '''
        Execute the `ls` command.
        '''
        try:
            self._sock.send(b'ls')

            # receive list of files on the server
            response = self.listen()
            if response == b'':
                self.exit_with_msg('Socket failure. Lost connection.', None)
            if response != None:
                filelist = response.decode('utf-8')
                print (filelist)
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)

    def exec_get(self, filename):
        '''
        Execute the `get` command.
        '''
        try:
            cmd = 'get ' + filename

            # send filename to server
            self._sock.send(str.encode(cmd))
            response = self.listen()

            if response == b'':
                self.exit_with_msg('Socket failure. Lost connection.', None)
            if response != None:   
                segs = response.split(b' ')
                received_hash = segs[0]
                file_bytes = b' '.join(segs[1:])

                file_hash = hashlib.sha256()
                file_hash.update(file_bytes)
                
                if received_hash == str.encode(file_hash.hexdigest()):
                    self.save_received_message(filename, file_bytes)
                else:
                    self.print_error('Recieved file differs from expected value. File may have been altered')
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)

    def exec_put(self, filename):
        '''
        Execute the `put` command.
        '''
        try:
            file_bytes = b''
            file_hash = hashlib.sha256()

            # read file contents
            file_path = os.path.join(self.FILE_DIR, filename)
            with open(file_path, 'rb') as f:
                file_bytes = bytes(f.read())
                file_hash.update(file_bytes)

            # format message to send to server
            payload = b'put ' + str.encode(filename) + b' ' + str.encode(file_hash.hexdigest()) + b' ' + file_bytes
            self._sock.sendall(payload)
            response = self.listen()
            if response == b'':
                self.exit_with_msg('Socket failure. Lost connection.', None)
            if response != None:
                print (response.decode('utf-8'))
        except FileNotFoundError:
            self.print_error(filename + ' does not exist.')
        except IOError as io_error:
            self.print_error('Reading file {} failed. Error: {}'.format(filename, io_error))
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)

    def exec_exit(self):
        '''
        Execute the `exit` command.
        '''
        try:
            cmd = 'exit'
            self._sock.send(str.encode(cmd))
            response = self.listen()
            if response == b'':
                self.exit_with_msg('Socket failure. Lost connection.', None)
            if response != None:
                self._sock.close()
                self.exit_with_msg(response.decode('utf-8'), None)
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)

    def save_received_message(self, filename, text):
        '''
        Write message to disk.
        '''
        try:
            # save file contents to ./files directory
            file_path = os.path.join(self.FILE_DIR, filename)
            with open(file_path, 'wb') as f:
                f.write(text)
        except IOError as io_error:
            self.print_error('Writing to file {} failed. Error: {}'.format(filename, io_error))

    @staticmethod
    def print_supported_commands(pre_message):
        '''
        Print supported commands with optional pre-message.
        '''
        if pre_message != None:
            print('\n' + pre_message + '\n')
        print('The supported are as follows:')
        print('`put <filename>`: Upload and send <filename> to the server.')
        print('`get <filename>`: Download <filename> from the server.')
        print('`ls`: Print a list of files available to download.')
        print('`exit`: Exit running application.\n')

    @staticmethod
    def print_error(err):
        '''
        Print formatted error message.
        '''
        print('\n\nError: ' + err + '\n')

    def exit_with_msg(self, msg, err):
        '''
        Print message then exit.
        '''
        print ('\n\nProgram Exiting! ' + msg)

        if err:
            print ('Error recieved: {}'.format(err))

        if self._sock:
            self._sock.close()

        exit(0)

    def run(self):
        try:
            # open connection to server
            self.establish_connection()

            # print supported cmd's to user
            self.print_supported_commands('Welcome to our simple FTP client!')

            # prompt user for input
            while True:
                self.prompt()

        except KeyboardInterrupt:
            self.exit_with_msg('Closing client.', None)


if __name__ == '__main__':
    client = Client()
    client.run() 
