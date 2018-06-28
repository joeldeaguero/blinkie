import serial

serialBaud = 38400
serialTimeout = 3.0
#serialPort="/dev/ttyAMA0"
serialPort="/dev/serial0"

port = serial.Serial(serialPort, baudrate=serialBaud, timeout=serialTimeout)

while True:
    port.write("\r\nHello, world!")
    rcv = port.read(10)
    port.write("\r\nYou sent:" + repr(rcv))
