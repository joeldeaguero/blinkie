from __future__ import unicode_literals
import prompt_toolkit
from prompt_toolkit.application import Application
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, VSplit, HSplit
from prompt_toolkit.widgets import Box, Button, Frame, TextArea
import asyncio
import time

lineCount = 6
debugAxis = 0
debugSleep = 0.2
bytesSentText = TextArea(text="")
bytesReceivedText = TextArea(text="")


def handleHome():
    checkStatus(debugAxis)
    time.sleep(debugSleep)
    sendHome(debugAxis)

	
def handleStatus():
	checkStatus(debugAxis)
	
def handleClear():
	global bytesSentText
	global bytesReceivedText
	bytesSentText.text = ""
	bytesReceivedText.text = ""

# Key bindings.
kb = KeyBindings()

@kb.add('h')
def keyHome(event):
	handleHome()
	
@kb.add('s')
def keyStatus(event):
	handleStatus()
	
@kb.add('c')
def keyClear(event):
	handleClear()

# Layout for displaying hello world.
# (The frame creates the border, the box takes care of the margin/padding.)
testCommands = HSplit([
	Button("Home", handler=handleHome),
	Button("Status", handler=handleStatus),
	Button("Clear", handler=handleClear)
])
testCommandContainer = Box(
    Frame(testCommands, width=20, height=20)
)
sendMonitor = Box(
    Frame(bytesSentText, width=56, height=10)
)
recvMonitor = Box(
    Frame(bytesReceivedText, width=56, height=10)
)
bytesMonitor = Box(
    HSplit([
        TextArea(text="bytes sent"),
        sendMonitor, 
        TextArea(text="bytes received"),
        recvMonitor
    ])
)
clientArea = Box(
    VSplit([testCommands, bytesMonitor])
)

layout = Layout(container=clientArea)


@kb.add("c-c")
def _(event):
    " Quit when control-c is pressed. "
    event.app.exit()


# Build a main application object.
application = Application(layout=layout, key_bindings=kb, full_screen=True, mouse_support=True)


def main():
    init()

    # Tell prompt_toolkit to use asyncio.
    use_asyncio_event_loop()

    # Run application async.
    asyncio.get_event_loop().run_until_complete(
        application.run_async().to_asyncio_future()
    )


import argparse
import serial
import serial.threaded
import sys

# docs only specify 15, but that makes no sense
responseSizeExpected = 16
ser = None
buf = ""

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val  # return positive value as is



class SerialToGui(serial.threaded.Protocol):
    def __init__(self):
        pass

    def __call__(self):
        return self

    def connection_lost(self, exc):
        global bytesReceivedText
        prev = bytesReceivedText.text
        oldLines = prev.split("\n")
        num=len(oldLines)
        if (num > lineCount):
            newLines = "\n".join(oldLines[num-lineCount:])
        else:
            newLines = prev
        newLines += "connection lost\n"
        #print("connection_lost: {0}\n".format(exc))
        bytesReceivedText.text = newLines

    def connection_made(self, transport):
        global bytesReceivedText
        prev = bytesReceivedText.text
        oldLines = prev.split("\n")
        num=len(oldLines)
        if (num > lineCount):
            newLines = "\n".join(oldLines[num-lineCount:])
        else:
            newLines = prev
        newLines += "connection made\n"
        #print("connection_made: {0}\n".format(transport))
        bytesReceivedText.text = newLines

    def data_received(self, data):
        global bytesReceivedText
        bytesReceivedText.text = string.replace(bytesReceivedText.text[-32:], 
            "\n", "") + "\n" + data.hex()

def init():
    global ser

    parser = argparse.ArgumentParser(description="Simple serial terminal")

    parser.add_argument(
        "--serial-port",
        help="serial port name",
        default="/dev/serial0",
        dest="serialPort",
    )
    parser.add_argument(
        "--baud-rate",
        type=int,
        nargs="?",
        help="set baud rate, default: %(default)s",
        default=1200,
        dest="baudRate",
    )
    group = parser.add_argument_group("serial port")

    group.add_argument(
        "--parity",
        choices=["N", "E", "O", "S", "M"],
        type=lambda c: c.upper(),
        help="set parity, one of {N E O S M}, default: N",
        default="N",
    )

    group.add_argument(
        "--rtscts",
        action="store_true",
        help="enable RTS/CTS flow control (default off)",
        default=False,
    )

    group.add_argument(
        "--xonxoff",
        action="store_true",
        help="enable software flow control (default off)",
        default=True,
    )

    group.add_argument(
        "--rts",
        type=int,
        help="set initial RTS line state (possible values: 0, 1)",
        default=None,
    )

    group.add_argument(
        "--dtr",
        type=int,
        help="set initial DTR line state (possible values: 0, 1)",
        default=None,
    )

    group = parser.add_argument_group("network settings")

    args = parser.parse_args()

    if args.rts is not None:
        serial.rts(args.rts)

    if args.dtr is not None:
        serial.dtr(args.dtr)

    try:
        ser = serial.Serial(
            port=args.serialPort,
            baudrate=args.baudRate,
            parity=args.parity,
            xonxoff=args.xonxoff,
            rtscts=args.rtscts,
            timeout=3.0
        )
    except serial.SerialException as e:
        errMsg = "Could not open serial port {}: {}\n".format(ser.name, e)
        sys.stderr.write(errMsg)
        sys.exit(1)

    #print("open")
    ser_to_gui = SerialToGui()
    serial_worker = serial.threaded.ReaderThread(ser, ser_to_gui)
    serial_worker.start()
    #print("listening")

# BCC lsb calculator to check communication integrity
def bcc_calc(bcc_int):
	bcc = (~bcc_int & 0xFFF) + 1        # 2's complement calculation (= one's complement + 1)
	for i in range(11, 7, -1):
		if bcc > 2**i:
			bcc -= 2**i                 # takes the LSB of the integer
	bcc = hex(bcc).upper()[2:]          # converts the integer to hex characters
	if len(bcc) == 1: bcc = '0' + bcc   # protocol needs BCC to be two characters
	return bcc
        
def makeCommand(a, b, c, d, e, f, g, h, i, j, k, l):
    bcc_int = 0
    bcc_int += ord(a)
    bcc_int += ord(b)
    bcc_int += ord(c)
    bcc_int += ord(d)
    bcc_int += ord(e)
    bcc_int += ord(f)
    bcc_int += ord(g)
    bcc_int += ord(h)
    bcc_int += ord(i)
    bcc_int += ord(j)
    bcc_int += ord(k)
    bcc_int += ord(l)
    bcc = bcc_calc(bcc_int)
    return bytes([
		ord(a[0]),
		ord(b[0]),
		ord(c[0]),
		ord(d[0]),
		ord(e[0]),
		ord(f[0]),
		ord(g[0]),
		ord(h[0]),
		ord(i[0]),
		ord(j[0]),
		ord(k[0]),
		ord(l[0]),
        ord(bcc[0]),
        ord(bcc[1])
    ])


# axis: 0-15
def checkStatus(axis):
    sendStringCommand(
        makeCommand(
            chr(ord("0") + axis), "n", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"
        )
    )
    return True


def send(str):
    global bytesSentText
    global ser
    prev = bytesSentText.text
    oldLines = prev.split("\n")
    num=len(oldLines)
    if (num > lineCount):
        newLines = "\n".join(oldLines[num-lineCount:])
    else:
        newLines = prev
    my_str_as_bytes = str
    newLines += "{0}\n".format(my_str_as_bytes.hex())
    bytesSentText.text = newLines
    ser.write(my_str_as_bytes)


def sendStringCommand(cmd):
	myBytes = bytes([2])
	for i,c in enumerate(cmd):
		myBytes += bytes([c])
	myBytes += bytes([3])
	send(myBytes)


def sendHome(axis):
	sendStringCommand(
		makeCommand(chr(ord("0") + axis), "o", "0", "7", "0","0","0","0","0","0","0","0")
		)

def bccChecker():
	print(makeCommand("1","Q","3","0","1","0","6","0","0","0","0","0"))
	
bccChecker()
main()
