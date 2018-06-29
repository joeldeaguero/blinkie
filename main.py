import serial

serialBaud = 38400
serialTimeout = 3.0
#serialPort="/dev/ttyAMA0"
serialPort="/dev/serial0"
#serialPort="COM1"

port = serial.Serial(serialPort, baudrate=serialBaud, timeout=serialTimeout)

def test():
    port.write("\r\nHello, world!")
    rcv = port.read(10)
    port.write("\r\nYou sent:" + repr(rcv))

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def makeCommand(a, b, c, d, e, f, g, h, i, j, k, l):
	sum = (
		ord(a) + 
		ord(b) + 
		ord(c) + 
		ord(d) + 
		ord(e) + 
		ord(f) + 
		ord(g) + 
		ord(h) + 
		ord(i) + 
		ord(j) + 
		ord(k) + 
		ord(l)
	)
	comp = twos_comp(sum, 16)
	check = comp & 0xff
	c_hi = (check >> 8) & 0xf
	c_lo = check & 0xf
	return "%c%c%c%c%c%c%c%c%c%c%c%c%c".format(
		a,
		b,
		c,
		d,
		e,
		f,
		g,
		h,
		i,
		j,
		k,
		l,
		chr(c_hi),
		chr(c_lo))

# axis: 0-15
def checkStatus(axis):
	sendStringCommand(makeCommand(chr(ord('0') + axis), 
		'n', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'))
	return True

def send(str):
	port.write(str)

def sendStringCommand(cmd):
	send("%c%s%c".format(2, cmd, 3))

def sendHome():
	sendStringCommand("3o070000000077")

def sendTestCommand():
	checkStatus(0)
	#sendHome()

#while True:
	#test()
sendTestCommand()

