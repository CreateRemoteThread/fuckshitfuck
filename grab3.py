#!/usr/bin/python

import time
from picoscope import ps2000a
import binascii
import os
import getopt
import sys
import serial
import numpy as np

SAMPLE_RATE = 40E6
NUM_SAMPLES = 5000
NUM_CAPTURES = 10000

def encryptAndTrace(ps,in_string):
  ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=100,enabled=True)
  ps.runBlock()
  ser.write(in_string)
  ps.waitReady()
  decrypt_text = ser.readline().rstrip()
  dataA = ps.getDataV('A',nSamples,returnOverflow=False)
  return dataA
  # f = open(fname,"w")
  # for i in range(0,nSamples):
  #   f.write("%s,%s\n" % (dataA[i],dataB[i]))
  # f.close()
  # print "%s:%s" % (in_string.rstrip(),decrypt_text)
  # return decrypt_text

if __name__ == "__main__":
  ps = ps2000a.PS2000a()
  ps.setChannel('A','DC',VRange=0.1,VOffset=0.0,enabled=True,BWLimited=False)
  ps.setChannel('B','DC',VRange=7.0,VOffset=0.0,enabled=True,BWLimited=False)
  nSamples = NUM_SAMPLES
  ps.setSamplingFrequency(SAMPLE_RATE,nSamples)
  ser = serial.Serial('/dev/ttyUSB0',9600)
  if sys.argv[1] == "s":
    traces = np.zeroes((NUM_SAMPLES,1),float32)
    data = np.zeroes((16,1),uint8)
    output_string = "e112233445566778899aabbccddeeff00\n"
    traces[:,0] = encryptAndTrace(ps,output_string)
    data[:,0] = [0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff]
    np.savez(sys.argv[2],traces=traces,data=data)
  elif sys.argv[1] == "r":
    traces = np.zeroes((NUM_SAMPLES,1),float32)
    data = np.zeroes((16,1),uint8)
    rand_input = os.urandom(16)
    output_string = "e" + binascii.hexlify(rand_input) + "\n"
    # encryptAndTrace(ps,output_string)
    traces[:,0] = encryptAndTrace(ps,output_string)
    data[:,0] = rand_input
    np.savez(sys.argv[2],traces=traces,data=data)
  elif sys.argv[1] == "x":
    traces = np.zeroes((NUM_SAMPLES,NUM_CAPTURES),float32)
    data = np.zeroes((16,NUM_CAPTURES),uint8)
    for i in range(0,NUM_CAPTURES):
      rand_input = os.urandom(16)
      output_string = "e" + binascii.hexlify(rand_input) + "\n"
      time.sleep(0)
      # encryptAndTrace(ps,output_string)
      traces[:,i] = encryptAndTrace(ps,output_string)
      data[:,i] = rand_input
    np.savez(sys.argv[2],traces=traces,data=data)
  ser.close()
  ps.stop()
  ps.close()
