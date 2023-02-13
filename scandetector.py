# Author: Eric Slick
# Assignment: Homework 2: Portscan Detector
# Date 2/20/21


import _thread
import time
import socket
import select


#           FIRST THREAD            #
# For every connection from <SrcIP, srcPort> to <dstIP, dstPort>, record <(SrcIP, dstIP, dstPort>), timestamp>
# Store "first contact connection" for 5 minutes before deleting. If first contact already exists, ignore it.
# Make a table (hashtable) for each first contact connection, per source, with their updated timestamp per 5 min
# First contacts that are older than 5 min need to be deleted, may need another thread.

#           SECOND THREAD           #
# Calculate the fan out rate of each source ip. Fan out rate is the rate of new connections per time interval.
# Ex: 5s fan out rate means the source host has made 5 first contact connections in the last second.
# Calculate the fan out rate for 3 intervals: per second, per minute, per 5 minutes.
# IF fan out rate per second exceeds 5, fan out rate per minute exceeds 100, or fan out rate per 5min exceed 300
# the source IP is identified as a port scanner.
# The program MUST output the source IP, the AVERAGE fan out rate per second, min, 5min, every 5 minutes
# FOR EVERY PORT SCANNER.

def port_watcher():
    # open 1-1024 ports?
    # Make a container to hold all of the sockets
    count = 0
    same_connections = []
    sockets = []
    connections = {}
    ip_container = []
    # Make a container to hold first-contact information
    connection_list = []
    # For some reason select.select() breaks when I make this value any higher than 1022
    # I think it may have something to do with my socket FD being 1024 at 1022. Not sure why that is either.
    for i in range(1, 1022):
        # AF_INET specifies IPV4, SOCK_STREAM specifies TCP
        address = ("127.0.0.1", i)
        sock = socket.create_server(address, family=socket.AF_INET, dualstack_ipv6=False)
        sock.listen(5)
        sockets.append(sock)
    while True:
        readable, _, _ = select.select(sockets, [], [])
        ready_server = readable[0]

        connection, address = ready_server.accept()

        tArr = []
        tArr.append(connection.getsockname())
        torf = evaluate_first_contact(connection_list, tArr)
        if torf == 1:
            same_connections.append((connection.getsockname(), time.localtime()))
            sec_val = fan_rate_sec(time.localtime().tm_sec, same_connections, tArr)
            min_val = fan_rate_min(time.localtime().tm_min, same_connections, tArr)
            five_min_val = fan_rate_hr(time.localtime().tm_hour, same_connections, tArr)
            if sec_val > 5:
                print("Second fanrate exceeded.")
                print("Average fanrate: {}".format((sec_val+min_val+five_min_val)/3))
                break
            if min_val > 100:
                print("Minute fanrate exceeded.")
                print("Average fanrate: {}".format((sec_val + min_val + five_min_val) / 3))
                break
            if five_min_val > 300:
                print("Five Minute fanrate exceeded.")
                print("Average fanrate: {}".format((sec_val + min_val + five_min_val) / 3))
                break
            continue
        if torf == -1:
            connection_list.append((connection.getsockname(), connection.getpeername(), time.localtime()))
            # To keep track of the amount of time passed since the new connection and delete it if necessary
            _thread.start_new_thread(time_tracker(connection_list[count][0], time.localtime().tm_min, connection_list, count, 1), ("Thread-1", 5, ))
            count += 1
        outputs(connection_list, sec_val, min_val, five_min_val)


# Print the outputs
def outputs(conn_list, fr_sec, fr_min, fr_five):
    for i in conn_list:
        print("Source IP: {}\n".format(i[0]))
        print("Fanrates: {}, {}, {}".format(fr_sec, fr_min, fr_five))


def fan_rate_sec(time_interval, conn_list, tArr):
    fanrate = 0
    for i in range(len(conn_list)):
        if conn_list[i][0] == tArr[0]:
            if conn_list[i][1] > time_interval:
                fanrate += 1
                continue
    if fanrate > 5:
        print("Fan rate exceeded, reason being, fanrate value is: {}".format(fanrate))
    return fanrate


def fan_rate_min(time_interval, conn_list, tArr):
    fanrate = 0
    for i in range(len(conn_list)):
        if conn_list[i][0] == tArr[0]:
            if conn_list[i][1] > time_interval:
                fanrate += 1
                continue
    if fanrate > 100:
        print("Fan rate exceeded, reason being, fanrate value is: {}".format(fanrate))
    return fanrate


def fan_rate_5min(time_interval, conn_list, tArr):
    fanrate = 0
    for i in range(len(conn_list)):
        if conn_list[i][0] == tArr[0]:
            if conn_list[i][1] > time_interval:
                fanrate += 1
                continue
    if fanrate > 300:
        print("Fan rate exceeded, reason being, fanrate value is: {}".format(fanrate))
    return fanrate


# This successfully evaluates if the ip/port is already listed in the container
def evaluate_first_contact(conn_list, tArr):
    for i in range(len(conn_list)):
        if conn_list[i][0] == tArr[0]:
            print("First contact exists")
            return 1
    return -1


# This needs to be in it's own thread
def time_tracker(fc_info, fc_time, fc_container, index, time_val):
    while fc_time != (fc_time+time_val):
        continue
    print("Time exceeded for: {}".format(fc_info))
    fc_container.pop(index)


port_watcher()
