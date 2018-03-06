#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket

class Client(object):

    ERROR_MSG_PREFIX = b'0000'

    def __init__(self):
        self._sock = None
        self._port = None
        self._ip_addr = None

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
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(10)
            self._sock.connect((self._ip_addr, self._port))

        except ConnectionRefusedError:
            self.exit_with_msg('Connection refused. Please check IP Address and port are correct and try again.', None)
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)

    # prompt user for input
    def prompt(self):
        raw_in = input('cmd: ')
        input_tuple = self.parse_input(raw_in)
        if input_tuple != False:
            self.process_input(input_tuple)

    # split input string into command and optional filename tuple
    def parse_input(self, args):
        segs = args.split(' ')

        # define command to execute
        cmd = segs[0].lower()

        # ensure 2nd argument is optionally defined
        filename = ''
        if cmd == 'put' or cmd == 'get':
            filename = segs[1]

        if filename.find('/') != -1:
            self.print_error('A <filename> with no path must be provided for this type of command.')
            return False

        return (cmd, filename)

    # process input
    def process_input(self, input_tuple):

        # process cmd
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

    # listen for a response on the open socket
    def listen(self):
        try:
            buff_size = 1024
            payload = b''
            listening = True
            while listening:
                seg = self._sock.recv(1024)
                payload += seg
                if len(seg) < buff_size:
                    listening = False

            if payload[0:4] == self.ERROR_MSG_PREFIX:
                self.print_error(payload[5:].decode('utf-8'))
            else:
                return payload
        except socket.timeout:
            self.print_error('No response from Server. Try again.')

    # execute the `ls` command
    def exec_ls(self):
        try:
            self._sock.send(b'ls')
            response = self.listen()
            if response == b'':
                self.exit_with_msg('Socket failure. Lost connection.', None)
            if response != None:
                filelist = response.decode('utf-8')
                print (filelist)
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)

    # execute the `get` command
    def exec_get(self, filename):
        try:
            cmd = 'get ' + filename
            self._sock.send(str.encode(cmd))
            response = self.listen()
            if response == b'':
                self.exit_with_msg('Socket failure. Lost connection.', None)
            if response != None:
                self.save_received_message(filename, response)
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)

    # execute the `put` command
    def exec_put(self, filename):
        try:
            file_bytes = b''
            with open(filename, 'rb') as f:
                file_bytes = bytes(f.read())

            payload = b'put ' + str.encode(filename) + b' ' + file_bytes
            self._sock.send(payload)
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

     # execute the `exit` command
    def exec_exit(self):
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

    # write message to disk
    def save_received_message(self, filename, text):
        try:
            with open(filename, 'wb') as f:
                f.write(text)
        except IOError as io_error:
            self.print_error('Writing to file {} failed. Error: {}'.format(filename, io_error))

    # Print supported commands with optional pre-message
    @staticmethod
    def print_supported_commands(pre_message):
        if pre_message != None:
            print('\n' + pre_message + '\n')
        print('The supported are as follows:')
        print('`put <filename>`: Upload and send <filename> to the server.')
        print('`get <filename>`: Download <filename> from the server.')
        print('`ls`: Print a list of files available to download.')
        print('`exit`: Exit running application.\n')

    # Print formatted error message
    @staticmethod
    def print_error(err):
        print('\n\nError: ' + err + '\n')

    # Print message then exit
    def exit_with_msg(self, msg, err):
        print ('\n\nProgram Exiting; ' + msg)

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
