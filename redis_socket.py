import socket

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
sock.connect(('127.0.0.1',6379))

print sock.family
print sock.type
print sock.proto

sock.send('get a\n')
data = sock.recv(1024)

print data

print type(data)
