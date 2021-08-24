import bluetooth

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

bd_addr = "B8:27:EB:1F:9C:84"
port = 1
server_sock.bind(("",port))
server_sock.listen(1)


sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))

sock.send("hello!!")

sock.close()