#!/usr/bin/env python3

# use with chrysanthemum bitstream

import sys
import getopt
import serial

CMD_PING = b'\x01'
CMD_READ = b'\x02'
CMD_WRITE = b'\x03'
CMD_ARM = b'\x04'
CMD_DISARM = b'\x05'

PARAM_CLKEDGES = b'\x01'
PARAM_IOEDGES = b'\x02'

RESP_ACK = b'0xAA'
RESP_NACK = b'0xFF'

if len(sys.argv) == 2:
  ser = serial.Serial(sys.argv[1],115200)
else:
  ser = serial.Serial("/dev/ttyUSB1",115200)
  
ser.write(CMD_PING)
b = ser.read(1)
if b != b'\xAA':
  print("CMD_PING failed. Wrong target or needs reflashing.")
  ser.close()
  sys.exit(0)

def readIoEdges(ser):
  a = 0
  ser.write(CMD_READ + PARAM_IOEDGES + b'\x00')
  a += ord(ser.read(1))
  ser.write(CMD_READ + PARAM_IOEDGES + b'\x01')
  a += ord(ser.read(1)) * 0x100
  ser.write(CMD_READ + PARAM_IOEDGES + b'\x02')
  a += ord(ser.read(1)) * 0x10000
  ser.write(CMD_READ + PARAM_IOEDGES + b'\x03')
  a += ord(ser.read(1)) * 0x1000000
  return a

def readClkEdges(ser):
  a = 0
  ser.write(CMD_READ + PARAM_CLKEDGES + b'\x00')
  a += ord(ser.read(1))
  ser.write(CMD_READ + PARAM_CLKEDGES + b'\x01')
  a += ord(ser.read(1)) * 0x100
  ser.write(CMD_READ + PARAM_CLKEDGES + b'\x02')
  a += ord(ser.read(1)) * 0x10000
  ser.write(CMD_READ + PARAM_CLKEDGES + b'\x03')
  a += ord(ser.read(1)) * 0x1000000
  return a

def squish(b1,b2):
  return bytes( [(ord(b1) << 4) + b2] )

def writeIoEdges(ser,value):
  ser.write(CMD_WRITE + squish(PARAM_IOEDGES,0) + bytes( [value & 0xFF ]))
  ser.read(1)
  ser.write(CMD_WRITE + squish(PARAM_IOEDGES,1) + bytes( [(value >> 8) & 0xFF]))
  ser.read(1)
  ser.write(CMD_WRITE + squish(PARAM_IOEDGES,2) + bytes( [(value >> 16) & 0xFF]))
  ser.read(1)
  ser.write(CMD_WRITE + squish(PARAM_IOEDGES,3) + bytes( [(value >> 24) & 0xFF]))
  ser.read(1)

def writeClkEdges(ser,value):
  ser.write(CMD_WRITE + squish(PARAM_CLKEDGES,0) + bytes( [value & 0xFF ]))
  ser.read(1)
  ser.write(CMD_WRITE + squish(PARAM_CLKEDGES,1) + bytes( [(value >> 8) & 0xFF]))
  ser.read(1)
  ser.write(CMD_WRITE + squish(PARAM_CLKEDGES,2) + bytes( [(value >> 16) & 0xFF]))
  ser.read(1)
  ser.write(CMD_WRITE + squish(PARAM_CLKEDGES,3) + bytes( [(value >> 24) & 0xFF]))
  ser.read(1)

print("io <ioedges> / clk <clkedges> / a / d / r");

print("Clk: %d" % readClkEdges(ser))
print("Io: %d" % readIoEdges(ser))

while True:
  cmd = input(" > ").rstrip().lstrip()
  tokens = cmd.split(" ")
  if tokens[0] == "io" and len(tokens) == 2:
    writeIoEdges(ser,int(tokens[1]))
    print("Io: %d" % readIoEdges(ser))
  elif tokens[0] == "clk" and len(tokens) == 2:
    writeClkEdges(ser,int(tokens[1]))
    print("Clk: %d" % readClkEdges(ser))
  elif tokens[0] in ("arm","a"):
    print("Arming!")
    ser.write(CMD_ARM)
    ser.read(1)
  elif tokens[0] in ("disarm","d"):
    print("Disarming!")
    ser.write(CMD_DISARM)
    ser.read(1)
  elif tokens[0] in ("read","r"):
    print("Clk: %d" % readClkEdges(ser))
    print("Io: %d" % readIoEdges(ser))
  elif tokens[0] in ("quit","q"):
    print("Bye!")
    ser.close()
    sys.exit(0)

ser.close()