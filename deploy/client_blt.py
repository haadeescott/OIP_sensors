import bluetooth
import time

bd_addr = "B8:27:EB:1F:9C:84"
client_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
port = 1
port2 = 2


server_sock.bind(("",port2))
server_sock.listen(1)
otherClient_sock, address = server_sock.accept()

client_sock.connect((bd_addr, port))


test = "012"

client_sock.send(test)




# data = otherClient_sock.recv(1024)
# print("received [%s]" % data)

client_sock.close()
server_sock.close()