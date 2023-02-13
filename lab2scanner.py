# Lab 2: Port Scanning, Cybersecurity Programming
# Author: Eric Slick
# Date 2/6/2021
# Status: Working, I think

import socket
import time
from time import sleep

tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

target = input("[+] Enter Target IP: ")


def udp_scanner(port):
    # Setting timeout value for the UDP message
    timeout = time.time() + 1
    try:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ack = bytes("Acknowledgement", "utf-8")
        for i in range(1, 1024):
            # Checking if the UDP message has sent fully by evaluating byte size
            if ack == (udp_sock.sendto(ack, port, i)):
                print('[*] Port', portNumber, '/udp', 'is open')
            # Checking if the UDP message has timed out, small number for testing purposes
            elif time.time() >= timeout:
                print('[*] Port', portNumber, '/udp', 'is closed')
        udp_sock.connect((target, port))
        udp_sock.close()
        return True
    except:
        return False


def tcp_scanner(port, wait_time):
    try:
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect((target, port))
        tcp_sock.close()
        return True
    except:
        return False


for portNumber in range(1, 1024):
    sleep(.002)
    if tcp_scanner(portNumber):
        print('[*] Port', portNumber, '/tcp', 'is open')
    udp_scanner(portNumber)


