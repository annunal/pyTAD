import socket

import time

HOST = '192.168.1.100'    # The remote host

PORT = 6722              # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((HOST, PORT))
#s.send('11*')  #jog channel 1

s.send('11')  #turn on channel 1

time.sleep (1)

s.send('21')  #turn off channel 1
time.sleep (2)

s.send('12*')  #jog channel 2

#s.send('12')  # turn on channel 2

#time.sleep (1)

#s.send('22')  #turn off channel 2
data = s.recv(1024)

data = s.recv(1024)
s.close()

print 'Received', repr(data)

