#!/usr/bin/python

import time
from picoscope import ps2000a
import binascii
import os
import sys
import serial

if __name__ == "__main__":
  ps = ps2000a.PS2000a()
  ps.setChannel('A','DC',VRange=0.05,VOffset=0.0,enabled=True,BWLimited=False)
  ps.setChannel('B','DC',VRange=7.0,VOffset=0.0,enabled=True,BWLimited=False)
  nSamples = 400000
  ps.setSamplingFrequency(100E6,nSamples)
  ser = serial.Serial('/dev/ttyUSB0',9600)
  if sys.argv[1] == "s":
    output_string = "e112233445566778899aabbccddeeff00\n"
  else:
    output_string = "e" + binascii.hexlify(os.urandom(16)) + "\n"
  print "ENCRYPT: %s" % output_string.rstrip()
  ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=100,enabled=True)
  ps.runBlock()
  ser.write(output_string)
  ps.waitReady()
  print "DECRYPT: %s" % ser.readline().rstrip()
  ser.close()
  dataA = ps.getDataV('A',nSamples,returnOverflow=False)
  dataB = ps.getDataV('B',nSamples,returnOverflow=False)
  ps.stop()
  ps.close()
  f = open(sys.argv[2],"w")
  for i in range(0,nSamples):
    f.write("%s,%s\n" % (dataA[i],dataB[i]))
  f.close()
  
  
