#!/usr/bin/python

import time
from picoscope import ps2000a
import binascii
import os
import getopt
import sys
import serial
import numpy as np

SAMPLE_RATE = 64000000 
NUM_SAMPLES = 50000
NUM_CAPTURES = 1000
ANALOG_OFFSET = 0 # -0.175
WRITE_FILE = None
VRANGE_PRIMARY = 0.05 # check tis manually first

def fix_out(in_str):
  try:
    return [ord(p) for p in binascii.unhexlify(in_str.rstrip()[1:])]
  except:
    return [0.0 for x in range(0,16)]

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
    if dataB[i] > 3.0:
      countUseful += 1
  print "%d : %s:%s (approximately %d useful)" % (cnt,in_string.rstrip(),decrypt_text,countUseful)
  if decrypt_text[0] != 'e':
    print "device restarted, waitng for stability"
    ser.close()
    time.sleep(10.0)
    ser = serial.Serial('/dev/ttyUSB0',9600)
  return (dataA,fix_out(decrypt_text))

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
  return (dataA,fix_out(decrypt_text))
  # f = open(fname,"w")
  # for i in range(0,nSamples):
  #   f.write("%s,%s\n" % (dataA[i],dataB[i]))
  # f.close()
  # return decrypt_text

if __name__ == "__main__":
  optlist, args = getopt.getopt(sys.argv[1:],"s:n:c:o:w:",["sample_rate=","num_samples=","count=","offset=","write_file="])
  for arg,value in optlist:
    if arg in ("-s","--sample_rate"):
      SAMPLE_RATE = int(float(value))
    elif arg in ("-n","--num_samples"):
      NUM_SAMPLES = int(value);
    elif arg in ("-c","--count"):
      NUM_CAPTURES = int(value);
    elif arg in ("-o","--offset"):
      ANALOG_OFFSET = float(value)
    elif arg in ("-w","--write_file"):
      WRITE_FILE = value
  if WRITE_FILE is None:
    print "fatal, you MUST specify an output file via -w"
    sys.exit(0)
  print "WRITE_FILE = %s" % WRITE_FILE
  print "SAMPLE_RATE = %d" % SAMPLE_RATE
  print "NUM_SAMPLES = %d" % NUM_SAMPLES
  print "NUM_CAPTURES = %d" % NUM_CAPTURES
  print "ANALOG_OFFSET = %f" % ANALOG_OFFSET
  ps = ps2000a.PS2000a()
  # use the finest resolution v-offset you cna.
  ps.setChannel('A','DC',VRange=VRANGE_PRIMARY,VOffset=ANALOG_OFFSET,enabled=True,BWLimited=False)
  ps.setChannel('B','DC',VRange=7.0,VOffset=0.0,enabled=True,BWLimited=False)
  nSamples = NUM_SAMPLES
  (freq,maxSamples) = ps.setSamplingFrequency(SAMPLE_RATE,nSamples)
  print "Actual frequency %d Hz" % freq
  ser = serial.Serial('/dev/ttyUSB0',9600)
  if NUM_CAPTURES == 1:
    traces = np.zeros((1,NUM_SAMPLES),np.float32)
    data = np.zeros((1,16),np.uint8)
    data_out = np.zeros((1,16),np.uint8)
    output_string = "e112233445566778899aabbccddeeff00\n"
    traces[0,:],data_out[0,:] = encryptAndTrace_2CH(ps,output_string,0)
    data[0,:] = [0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff,0x00]
    # np.savez(sys.argv[2],traces=traces,data=data,data_out=data_out)
  else:
    traces = np.zeros((NUM_CAPTURES,NUM_SAMPLES),np.float32)
    data = np.zeros((NUM_CAPTURES,16),np.uint8)
    data_out = np.zeros((NUM_CAPTURES,16),np.uint8)
    for i in range(0,NUM_CAPTURES):
      rand_input = os.urandom(16)
      output_string = "e" + binascii.hexlify(rand_input) + "\n"
      time.sleep(0.1)
      # encryptAndTrace(ps,output_string)
      traces[i,:],data_out[i,:] = encryptAndTrace(ps,output_string,i)
      data[i,:] = [ord(x) for x in rand_input]
  ser.close()
  ps.stop()
  ps.close()
  print "Closing interfaces and saving, OK to unplug..."
  np.savez(WRITE_FILE,traces=traces,data=data,data_out=data_out)
