#!/usr/bin/python

import time
from picoscope import ps2000a
import binascii
import os
import sys
import serial

def encryptAndTrace(ps,in_string,fname):
  # print "ENCRYPT: %s" % in_string.rstrip()
  ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=100,enabled=True)
  ps.runBlock()
  ser.write(in_string)
  ps.waitReady()
  decrypt_text = ser.readline().rstrip()
  dataA = ps.getDataV('A',nSamples,returnOverflow=False)
  dataB = ps.getDataV('B',nSamples,returnOverflow=False)
  f = open(fname,"w")
  for i in range(0,nSamples):
    f.write("%s,%s\n" % (dataA[i],dataB[i]))
  f.close()
  print "%s:%s" % (in_string.rstrip(),decrypt_text)
  return decrypt_text

if __name__ == "__main__":
  ps = ps2000a.PS2000a()
  # higher voltage offset for channel A to trace all the things...
  ps.setChannel('A','DC',VRange=0.1,VOffset=0.0,enabled=True,BWLimited=False)
  ps.setChannel('B','DC',VRange=7.0,VOffset=0.0,enabled=True,BWLimited=False)
  nSamples = 200000
  ps.setSamplingFrequency(40E6,nSamples)
  ser = serial.Serial('/dev/ttyUSB0',9600)
  if sys.argv[1] == "s":
    output_string = "e112233445566778899aabbccddeeff00\n"
    encryptAndTrace(ps,output_string,sys.argv[2])
  elif sys.argv[1] == "r":
    output_string = "e" + binascii.hexlify(os.urandom(16)) + "\n"
    encryptAndTrace(ps,output_string,sys.argv[2])
  elif sys.argv[1] == "x":
    for i in range(0,200):
      in_rand = binascii.hexlify(os.urandom(16))
      output_string = "e" + in_rand + "\n"
      fn = "%s/%s.csv" % (sys.argv[2],in_rand)
      encryptAndTrace(ps,output_string,fn)
  ser.close()
  ps.stop()
  ps.close()
