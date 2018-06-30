from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, VSplit, HSplit
from prompt_toolkit.widgets import Box, Button, Frame, TextArea
import asyncio

lineCount = 6

def handleHome():
    checkStatus(0)
    sendHome()

# Layout for displaying hello world.
# (The frame creates the border, the box takes care of the margin/padding.)
testCommands = HSplit([
    Button("home", handler=handleHome)
])
testCommandContainer = Box(
    Frame(testCommands, width=20, height=20)
)
bytesSentText = TextArea(text="")
sendMonitor = Box(
    Frame(bytesSentText, width=56, height=10)
)
bytesReceivedText = TextArea(text="")
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


# Key bindings.
kb = KeyBindings()


@kb.add("c-c")
def _(event):
    " Quit when control-c is pressed. "
    event.app.exit()


# Build a main application object.
application = Application(layout=layout, key_bindings=kb, full_screen=True)


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


def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val  # return positive value as is


def fcntl(fd, op, arg=0):
    return 0


def ioctl(fd, op, arg=0, mutable_flag=True):
    if mutable_flag:
        return 0
    else:
        return ""


def flock(fd, op):
    return


def lockf(fd, operation, length=0, start=0, whence=0):
    return


class SerialToGui(serial.threaded.Protocol):
    def __init__(self):
        pass

    def __call__(self):
        return self

    def data_received(self, data):
		global bytesReceivedText
		prev = bytesReceivedText.text
		oldLines = prev.split("\n")
		num=len(oldLines)
		if (num > lineCount):
			newLines = "\n".join(oldLines[num-lineCount:])
		else:
			newLines = prev
		my_str_as_bytes = data.encode()
		newLines += "{0}\n".format(my_str_as_bytes.hex())
		bytesReceivedText.text = newLines


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
        default="38400",
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
        default=False,
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
        )
    except serial.SerialException as e:
        errMsg = "Could not open serial port {}: {}\n".format(ser.name, e)
        sys.stderr.write(errMsg)
        sys.exit(1)

    ser_to_gui = SerialToGui()
    serial_worker = serial.threaded.ReaderThread(ser, ser_to_gui)
    serial_worker.start()


def makeCommand(a, b, c, d, e, f, g, h, i, j, k, l):
    sum = (
        ord(a)
        + ord(b)
        + ord(c)
        + ord(d)
        + ord(e)
        + ord(f)
        + ord(g)
        + ord(h)
        + ord(i)
        + ord(j)
        + ord(k)
        + ord(l)
    )
    comp = twos_comp(sum, 16)
    check = comp & 0xff
    c_hi = (check >> 8) & 0xf
    c_lo = check & 0xf
    return "%s%s%s%s%s%s%s%s%s%s%s%s%x%x" % (
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
        c_hi,
        c_lo,
    )


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
    my_str_as_bytes = str.encode()
    newLines += "{0}\n".format(my_str_as_bytes.hex())
    bytesSentText.text = newLines
    ser.write(my_str_as_bytes)


def sendStringCommand(cmd):
    send("%c%s%c" % (chr(2), cmd, chr(3)))


def sendHome():
    sendStringCommand("3o070000000077")



main()
