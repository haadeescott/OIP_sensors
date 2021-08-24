import bluetooth

bd_addr = "B8:27:EB:1F:9C:84"

port = 1

sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))

sock.send("I love ken cock!!")

sock.close()