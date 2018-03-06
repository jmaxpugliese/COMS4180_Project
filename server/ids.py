#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket
import json
import binascii
import server
import datetime

ERROR_MSG_PREFIX = b'0000'

class Ids(object):
    PACKET_SIZE = 1024
    PATTERN_FILE = "pattern-config"
    LOG_FILE = "ids-log"

    def __init__(self):
        self._port = self.get_runtime_args()
        self._ip_addr = socket.gethostbyname(socket.gethostname())
        self._ssock = None

    # Retrieve and validate runtime arguments before starting the application
    def get_runtime_args(self):
        if len(sys.argv) != 2:
            self.exit_with_msg('Please specify input with format:\n`<connection-port>`\n', None)

        if not sys.argv[1].isdigit():
            self.exit_with_msg('Port must be an integer. Please try again.', None)

        port = int(sys.argv[1])
        if port < 0 or port > 65535:
            self.exit_with_msg('Port number must be betwen 0-65535.', None)
        
        return port

    def check_packet(self, pkt, connected_socket):
        hex_pkt = str(binascii.hexlify(pkt))
       
        try:
            with open(self.PATTERN_FILE, 'r') as patterns:
                data = json.load(patterns)
                for entry in data:
                    if data[entry] in hex_pkt:
                        try:
                            with open(self.LOG_FILE, 'a') as log_file:
                                log_file.write('Pattern ID: ' + entry + '; IP Address: ' + connected_socket + '; Timestamp: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n')
                        except IOError as io_error:
                                self.exit_with_msg('Writing to log file failed.', io_error)
                        return False
        except IOError as io_error:
            self.exit_with_msg('Reading pattern file failed.', io_error)
        
        return True

    def check_server_response(self, packet_data):
        msg = b''
        index = 0
        while index < len(packet_data):
            next_index = index+self.PACKET_SIZE
            if next_index < len(packet_data):
                seg = packet_data[index:index+self.PACKET_SIZE]
                index = next_index
            else:
                end_index = len(packet_data)-index
                seg = packet_data[index:end_index]
                index = len(packet_data)

            process_pkt = self.check_packet(seg, self._ip_addr)
            # inspect segment
            if process_pkt:
                msg += seg

        return msg

    # listen for messages on initialized port
    def listen(self, connected_socket, connected_client):
        # ensure the entire message is received before process
        buff_size = self.PACKET_SIZE
        msg = b''
        listening = True
        while listening:
            seg = connected_socket.recv(self.PACKET_SIZE)
            process_pkt = self.check_packet(seg, connected_client[0])
            # inspect segment
            if process_pkt:
                msg += seg

            if len(seg) < buff_size:
                listening = False

        return msg

    @staticmethod
    def send(response, connected_socket):
        print('Sending response: ' + response.decode("utf-8"))
        connected_socket.send(response)
       

    # initialize socket for incoming messages
    def init_socket(self):
        self._ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ssock.bind((self._ip_addr, self._port))
        self._ssock.listen(1)
        print ('IDS starting up on ip {} port {}'.format(self._ip_addr, self._port))
        connected_socket, connected_client = self._ssock.accept()
        print ('Connection from {}'.format(connected_client,))
        return connected_socket, connected_client

    def run(self):
         # start IDS
        
        connected_socket = None
        try:
            connected_socket, connected_client = self.init_socket()
            while True:
                # wait for message
                msg = self.listen(connected_socket, connected_client)

                # send message to server for processing
                byte_response = server.process(msg)

                if not byte_response:
                    self.send(b'Thank you!', connected_socket)
                    self.exit_with_msg('Closing server socket.', None)

                to_send = self.check_server_response(byte_response)

                # respond to client
                if to_send:
                    self.send(byte_response, connected_socket)
                else:
                    self.send(self.format_error('Unable to send server response.'), connected_socket)

        except KeyboardInterrupt:
            self.exit_with_msg('Closing server socket', None)
        except ConnectionResetError:
            self.exit_with_msg('Socket connection reset. Please start application again.', None)
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)
        except Exception as e:
            self.exit_with_msg('IDS failed. Please try again.', e)

        finally:
            if connected_socket:
                connected_socket.close()


    # Print message then exit
    def exit_with_msg(self, msg, err):
        print ('\nIDS & Server Exiting; ' + msg)
        
        if err:
            print ('Error recieved: {}'.format(err))
        
        if self._ssock:
             self._ssock.close()

        exit(0)

    @staticmethod
    def format_error(error_str):
        return ERROR_MSG_PREFIX + str.encode(error_str)

if __name__ == '__main__':
    ids = Ids()
    ids.run()        