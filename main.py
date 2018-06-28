import serial

serialBaud = 38400
serialTimeout = 3.0

port = serial.Serial("/dev/ttyAMA0", baudrate=serialBaud, timeout=serialTimeout)

while True:
    port.write("\r\nHello, world!")
    rcv = port.read(10)
    port.write("\r\nYou sent:" + repr(rcv))
