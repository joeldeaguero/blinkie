import serial

serialBaud = 38400
serialTimeout = 3.0
#serialPort="/dev/ttyAMA0"
serialPort="/dev/serial0"

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
	sum = a + b + c + d + e + f + g + h + i + j + k + l
	comp = twos_comp(sum, 16)
	check = comp & 255
	return "%c%c%c%c%c%c%c%c%c%c%c%c%c".format(a,b,c,d,e,f,g,h,i,j,k,l,check)

# axis: 0-15
def checkStatus(axis):
	sendStringCommand(makeCommand("%c".format("0" + axis), 
		"n", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"))
	return True

def sendStringCommand(cmd):
	if !checkStatus():
		return
	send("%c%s%c".format(2, cmd, 3))

def sendHome():
	sendStringCommand("3o070000000077")

def sendTestCommand():
	sendHome()

while True:
	#test()
	sendTestCommand()