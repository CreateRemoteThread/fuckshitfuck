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
NUM_SAMPLES = 300000
NUM_CAPTURES = 5000
ANALOG_OFFSET = -0.175

def encryptAndTrace_2CH(ps,in_string,cnt):
  global ser
  ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=100,enabled=True)
  ps.runBlock()
  ser.write(in_string)
  ps.waitReady()
  decrypt_text = ser.readline().rstrip()
  dataA = ps.getDataV('A',nSamples,returnOverflow=False)
  dataB = ps.getDataV('B',nSamples,returnOverflow=False)
  countUseful = 0
  for i in range(0,nSamples):
    if dataB[i] > 1.0:
      countUseful += 1
  print "%d : %s:%s (approximately %d useful)" % (cnt,in_string.rstrip(),decrypt_text,countUseful)
  if decrypt_text[0] != 'e':
    print "device restarted, waitng for stability"
    ser.close()
    time.sleep(10.0)
    ser = serial.Serial('/dev/ttyUSB0',9600)
  return dataA

def encryptAndTrace(ps,in_string,cnt):
  global ser
  ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=100,enabled=True)
  ps.runBlock()
  ser.write(in_string)
  ps.waitReady()
  decrypt_text = ser.readline().rstrip()
  dataA = ps.getDataV('A',nSamples,returnOverflow=False)
  print "%d : %s:%s" % (cnt,in_string.rstrip(),decrypt_text)
  if decrypt_text[0] != 'e' or len(decrypt_text) != 33:
    print "device restarted, waitng for stability"
    ser.close()
    time.sleep(10.0)
    ser = serial.Serial('/dev/ttyUSB0',9600)
  return dataA
  # f = open(fname,"w")
  # for i in range(0,nSamples):
  #   f.write("%s,%s\n" % (dataA[i],dataB[i]))
  # f.close()
  # return decrypt_text

if __name__ == "__main__":
  ps = ps2000a.PS2000a()
  # use the finest resolution v-offset you cna.
  ps.setChannel('A','DC',VRange=0.1,VOffset=ANALOG_OFFSET,enabled=True,BWLimited=False)
  ps.setChannel('B','DC',VRange=7.0,VOffset=0.0,enabled=True,BWLimited=False)
  nSamples = NUM_SAMPLES
  ps.setSamplingFrequency(SAMPLE_RATE,nSamples)
  ser = serial.Serial('/dev/ttyUSB0',9600)
  if sys.argv[1] == "s":
    traces = np.zeros((1,NUM_SAMPLES),np.float32)
    data = np.zeros((1,16),np.uint8)
    output_string = "e112233445566778899aabbccddeeff00\n"
    traces[0,:] = encryptAndTrace_2CH(ps,output_string,0)
    data[0,:] = [0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff,0x00]
    np.savez(sys.argv[2],traces=traces,data=data)
  elif sys.argv[1] == "r":
    traces = np.zeros((1,NUM_SAMPLES),np.float32)
    data = np.zeros((1,16),np.uint8)
    rand_input = os.urandom(16)
    output_string = "e" + binascii.hexlify(rand_input) + "\n"
    # encryptAndTrace(ps,output_string)
    traces[0,:] = encryptAndTrace_2CH(ps,output_string,0)
    data[0,:] = [ord(x) for x in rand_input]
    # data[0,:] = rand_input
    np.savez(sys.argv[2],traces=traces,data=data)
  elif sys.argv[1] == "x":
    traces = np.zeros((NUM_CAPTURES,NUM_SAMPLES),np.float32)
    data = np.zeros((NUM_CAPTURES,16),np.uint8)
    for i in range(0,NUM_CAPTURES):
      rand_input = os.urandom(16)
      output_string = "e" + binascii.hexlify(rand_input) + "\n"
      time.sleep(0.1)
      # encryptAndTrace(ps,output_string)
      traces[i,:] = encryptAndTrace(ps,output_string,i)
      data[i,:] = [ord(x) for x in rand_input]
    np.savez(sys.argv[2],traces=traces,data=data)
  ser.close()
  ps.stop()
  ps.close()
