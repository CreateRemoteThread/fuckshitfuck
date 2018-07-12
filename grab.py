#!/usr/bin/python

import time
from picoscope import ps2000a
import pylab as plt
import numpy as np
import sys
import serial
import binascii
import os

# ./grab.py s <blah>
# ./grab.py r <blah>

def usage():
  print "./grab.py s <file> = save single capture of static input"
  print "./grab.py r <file> = save single capture of random input"

if __name__ == "__main__":
  if len(sys.argv) != 3:
    usage()
    sys.exit(0)
  try:
    ps = ps2000a.PS2000a()
    # print ps.getAllUnitInfo()
  except:
    print "Error: Are you in the 'pico' group?"
    sys.exit(0)
  print "Calibrating initial power measurement..."
  ps.setChannel('A','DC',VRange=7.0,VOffset=0.0,enabled=True,BWLimited=False)
  ps.setSamplingFrequency(50E6,5000)
  ps.runBlock()
  ps.waitReady()
  res = ps.getDataV('A',1)
  vOffset = 0 - (int(res[0] * 1000.0) / 100.0)
  print "Voltage calibrated at %s" % vOffset
  channelRange = ps.setChannel('A','DC',VRange=5.0,VOffset=vOffset,enabled=True,BWLimited=False,probeAttenuation=10)
  print "Channel A Range: %d" % channelRange
  channelRange = ps.setChannel('B','DC',VRange=5.0,VOffset=vOffset,enabled=True,BWLimited=False,probeAttenuation=10)
  print "Channel B Range: %d" % channelRange
  nSamples = 4000000
  res = ps.setSamplingFrequency(100E6,nSamples)
  print "Sampling at %f MHz..." % (res[0] / 1E6)
  ser = serial.Serial('/dev/ttyUSB0',9600)
  if sys.argv[1] == "s":
    output_string = "e112233445566778899aabbccddeeff00\n"
  else:
    output_string = "e" + binascii.hexlify(os.urandom(16)) + "\n"
  print "ENCRYPT: %s" % (output_string)
  ps.runBlock()
  ser.write(output_string)
  ps.waitReady()
  dataA = ps.getDataV('A', nSamples, returnOverflow=False)
  dataB = ps.getDataV('B', nSamples, returnOverflow=False)
  ps.stop()
  ps.close()
  print "DECRYPT: %s" % ser.readline().rstrip()
  ser.close()
  f = open(sys.argv[2],"w")
  f.write("A,B,B-A\n")
  minA = 5.0
  maxA = 5.0
  for i in range(0,nSamples):
    s = (dataB[i] - dataA[i]) / 1.5
    if dataA[i] < minA:
      minA = dataA[i]
    elif dataA[i] > maxA:
      maxA = dataA[i]
    f.write("%s,%s,%s\n" % (dataA[i],dataB[i],s))
  f.close()
  print "Saved. Min %s, max %s" % (minA,maxA)
