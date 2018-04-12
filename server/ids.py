#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import json
import binascii
import server_wrapper
import datetime

ERROR_MSG_PREFIX = b'0000'
SUCCESS_MSG_PREFIX = b'1111'

class Ids(object):
    '''
    The Ids class establishes and maintains a connection with a client.
    The client sends requests that the ids screens for forbidden patterns
    within pattern-config. It will drop those packets and send the remaining
    the server to process (through server_wrapper). The ids will then format
    a reply for the client using the server's reponse, again screen for
    forbidden patterns, and send the packets that pass to the client.
    '''

    # mtu is 1500, subtract headers
    PACKET_SIZE = 1436
    PATTERN_FILE = "pattern-config"
    LOG_FILE = "ids-log"

    def __init__(self, port):
        self._port = port
        self._ip_addr = socket.gethostbyname(socket.gethostname())
        self._ssock = None

    def check_packet(self, pkt, connected_socket):
        '''
        Verify that packet does not contain any patterns in the pattern-config file.
        '''

        # convert packet contents to hex
        hex_pkt = str(binascii.hexlify(pkt))
        try:
            with open(self.PATTERN_FILE, 'r') as patterns:
                try:
                    data = json.load(patterns)
                except:
                    data = {}

                for entry in data:

                    # check if pattern is in packet
                    # if so write to log file and return false
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
        '''
        Read server response in packet-size segments and filter out
        packets with forbidden patterns in them.
        '''

        msg = b''
        index = 0
        while index < len(packet_data):
            next_index = index+self.PACKET_SIZE
            if next_index < len(packet_data):
                seg = packet_data[index:index+self.PACKET_SIZE]
                index = next_index
            # last packet
            else:
                end_index = len(packet_data)
                seg = packet_data[index:end_index]
                index = len(packet_data)

            # inspect segment
            process_pkt = self.check_packet(seg, self._ip_addr)
            if process_pkt:
                msg += seg

            # add EOF if last packet is dropped
            if index == len(packet_data) and not process_pkt:
                msg += b'\n'

        return msg

    def listen(self, connected_socket, connected_client):
        '''
        Listen for messages on initialized port.
        '''
        # entire message is received before process
        msg = b''
        listening = True
        while listening:
            seg = connected_socket.recv(self.PACKET_SIZE)

            # inspect segment
            process_pkt = self.check_packet(seg, connected_client[0])
            if process_pkt:
                msg += seg

            if len(seg) < self.PACKET_SIZE:
                listening = False

            # add EOF if last packet is dropped.
            if not listening and not process_pkt:
                msg += b'\n'

        return msg

    @staticmethod
    def send(response, connected_socket):
        '''
        Send data to client.
        '''
        
        print('Sending response to client.')
        connected_socket.sendall(response)

    def init_socket(self):
        '''
         Initialize socket for incoming messages from client.
        '''

        self._ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ssock.bind((self._ip_addr, self._port))
        self._ssock.listen(1)
        print ('IDS starting up on ip {} port {}'.format(self._ip_addr, self._port))
        connected_socket, connected_client = self._ssock.accept()
        print ('Connection from {}'.format(connected_client,))
        return connected_socket, connected_client

    def exit_with_msg(self, msg, err):
        '''
        Print message then exit.
        '''

        print ('\nIDS & Server Exiting; ' + msg)

        if err:
            print ('Error recieved: {}'.format(err))

        # close server socket
        if self._ssock:
             self._ssock.close()

        exit(0)

    @staticmethod
    def format_error(error_str):
        '''
        Add error code to server response.
        '''
        return ERROR_MSG_PREFIX + str.encode(error_str)

    def run(self):
        '''
        Run ids: initialize socket, wait for message, send to server
        for processing (after packet analysis), and send server response to
        client (after packet analysis).
        '''

        connected_socket = None
        try:
            connected_socket, connected_client = self.init_socket()
            while True:

                # wait for message
                msg = self.listen(connected_socket, connected_client)

                # send message to server for processing
                byte_response = server_wrapper.server_ids_relay(msg)

                # if 'None' is response from server, it means exit
                # command was sent.
                # Close server.
                if not byte_response:
                    self.send(SUCCESS_MSG_PREFIX + b'Thank you!', connected_socket)
                    self.exit_with_msg('Closing server socket.', None)

                # packets that passed analysis
                to_send = self.check_server_response(byte_response)

                # respond to client
                # b'\n' indicates that all the packets were dropped
                # no response needed for that case
                if to_send != b'\n':
                    self.send(to_send, connected_socket)
                else:
                    self.send(self.format_error('Unable to send server response.'), connected_socket)

        except KeyboardInterrupt:
            self.exit_with_msg('Closing server socket', None)
        # except ConnectionResetError:
        #     self.exit_with_msg('Socket connection reset. Please start application again.', None)
        except socket.error as err:
            self.exit_with_msg('Socket failure. Please start application again.', err)
        except Exception as e:
            self.exit_with_msg('IDS failed. Please try again.', e)

        finally:
            if connected_socket:
                connected_socket.close()

if __name__ == '__main__':
    ids = Ids()
    ids.run()
