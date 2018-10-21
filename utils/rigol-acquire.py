#!/usr/bin/python

# For DS1XXX series
# CHAN1 is source (10x)
# CHAN2 is trigger (1x, 2.0v active high)

import pwn
import sys
import time
import serial
import numpy as np

def convertToRawVoltage(in_byte):
  x = ord(in_byte)
  return np.float32( YORIGIN * YINCREMENT + x * YINCREMENT )

try:
  p = pwn.remote("10.10.10.4",5555)
except:
  print "Could not connect to scope"
  sys.exit(0)

SAMPLERATE=64000000
SAMPLECOUNT=30000000
TRACECOUNT=5

# put the scope in a known state
p.sendline(":STOP")
# set the vertical offset
p.sendline(":CHAN1:SCAL 0.01")
p.sendline(":CHAN1:OFFS -0.055")
p.sendline(":CHAN2:SCAL 5")
# set up a logic trigger on chan2
p.sendline(":TRIG:MODE EDGE")
p.sendline(":TRIG:EDGE:SOUR CHAN2")
p.sendline(":TRIG:EDGE:LEV 2.0")
p.sendline(":TRIG:EDGE:SWE SING")
p.sendline(":WAV:SOUR CHAN1")
p.sendline(":TIM:SCAL 0.001")
p.sendline(":TIM:SCAL?")
p.sendline(":ACQ:MDEP 6000000")
data = p.recv().rstrip()
print "Timebase is %s" % data

# p.sendline(":ACQ:MDEP?")
# data = p.recv().rstrip()
# print "Acquire Memory Depth is %d" % int(data)
p.sendline(":ACQ:SRAT?")
data = p.recv().rstrip()
print "Sample rate is %s" % data
p.sendline(":SINGLE")
ser = serial.Serial('/dev/ttyUSB0',9600)
while True:
  ser.write("e1122334455667788\n")
  time.sleep(1.0)
  p.sendline(":TRIG:STAT?")
  data = p.recv().rstrip()
  if data == "STOP":
    break
  else:
    print "Waiting for data acquire (%s)" % data
p.sendline(":WAV:SOUR CHAN1")
p.sendline(":WAV:YINC?")
data = p.recv().rstrip()
print "Y Increment is %s" % data
YINCREMENT = float(data)
p.sendline(":WAV:YOR?")
data = p.recv().rstrip()
print "Y Origin is %s" % data
YORIGIN = float(data)
p.sendline(":ACQ:MDEP?")
data = p.recv().rstrip()
print "Memory depth is %s" % data

p.sendline(":WAV:MODE RAW")
p.sendline(":WAV:FORM BYTE")
p.sendline(":WAV:FORM STAR 1")
p.sendline(":WAV:FORM STOP 125000")
p.sendline(":WAV:DATA?")
header = p.recv(11)
print "header: %s" % header
data = p.recvall(timeout=0.5)

voltageValues = [convertToRawVoltage(d) for d in data[:-1]]
print voltageValues

np.savez("test.npz",traces=[voltageValues],data=[["lol"]],data_out=[["sex"]],freq=[250000000])
# f = open("rigol.save","wb")
# f.write(data)
# f.close()
p.close()
