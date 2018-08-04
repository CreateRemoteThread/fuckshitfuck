#!/usr/bin/python

import time
from picoscope import ps2000a
import binascii
import os
import getopt
import sys
import serial
import numpy as np

SAMPLE_RATE = 20E6
NUM_SAMPLES = 3200000
NUM_CAPTURES = 1

if __name__ == "__main__":
  ps = ps2000a.PS2000a()
  ps.setChannel('A','DC',VRange=0.1,VOffset=-0.175,enabled=True,BWLimited=False)
  ps.setChannel('B','DC',VRange=5.0,VOffset=0.0,enabled=True,BWLimited=False)
  nSamples = NUM_SAMPLES
  ps.setSamplingFrequency(SAMPLE_RATE,nSamples)
  ser = serial.Serial('/dev/ttyUSB0',9600)
  traces = np.zeros((1,NUM_SAMPLES),np.float32)
  trigger = np.zeros((1,NUM_SAMPLES),np.float32)
  data = np.zeros((1,8),np.uint8)
  in_bytes = os.urandom(8)
  data_out = "r" + binascii.hexlify(in_bytes) + "\r\n"
  ps.runBlock()
  # ser.write(data_out)
  ps.waitReady()
  traces[0,:] = ps.getDataV('A',nSamples,returnOverflow=False)
  trigger[0,:] = ps.getDataV('B',nSamples,returnOverflow=False)
  data[0,:] = [ord(x) for x in in_bytes]
  np.savez(sys.argv[1],traces=traces,data=data,trigger=trigger)
  ser.close()
  ps.stop()
  ps.close()
