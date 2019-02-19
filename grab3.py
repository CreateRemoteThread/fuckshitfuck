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
NUM_SAMPLES = 200000
NUM_CAPTURES = 1
ANALOG_OFFSET = -0.09
# ANALOG_OFFSET = -0.006 # for ATMega test board
WRITE_FILE = None
# VRANGE_PRIMARY = 0.02 # for EM probe
VRANGE_PRIMARY = 0.05

RAND_LEN = 16
RAND_KEY = "e"
FIXED_PT = False

def fix_out(in_str):
  try:
    return [ord(p) for p in binascii.unhexlify(in_str.rstrip()[1:])[:RAND_LEN]]
  except:
    return [0.0 for x in range(0,RAND_LEN)]

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
  firstUseful = 0
  FIRST_USEFUL = 1
  for i in range(0,nSamples):
    if dataB[i] > 3.0:
      firstUseful += FIRST_USEFUL
      countUseful += 1
    elif firstUseful > 0:
      FIRST_USEFUL = 0
  print "%d : %s:%s (approximately %d useful, %d in first useful block)" % (cnt,in_string.rstrip(),decrypt_text,countUseful,firstUseful)
  if decrypt_text[0] != 'e':
    print "device restarted, waitng for stability"
    ser.close()
    time.sleep(5.0)
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
  if decrypt_text[0] != 'e' or len(decrypt_text) != (1 + RAND_LEN * 2):
    print "device restarted, waitng for stability"
    ser.close()
    time.sleep(10.0)
    ser = serial.Serial('/dev/ttyUSB0',9600)
  return (dataA,fix_out(decrypt_text))

def usage():
  print " grab3.py : part of the fuckshitfuck toolkit"
  print "----------------------------------------------"
  print " -h : prints this message"
  print " -r [samplerate] : set samplerate in hz"
  print " -n [samplecnt] : get this many samples per trace"
  print " -c [tracecnt] : get this many traces"
  print " -o [offset] : set picoscope analog offset"
  print " -w [outfile] : save traces to this file"
  print " -R : RSA ZERO KEY mode (static short plaintext)"
  print " -0 : RSA NONZERO KEY mode (static short plaintext)"
  print ""
  print " if -c is 1, extra info will be printed"

if __name__ == "__main__":
  optlist, args = getopt.getopt(sys.argv[1:],"0Rhr:n:c:o:w:",["RSANONZERO","RSA","help","samplerate=","samples=","count=","offset=","write_file="])
  for arg,value in optlist:
    if arg in ("-h","--help"):
      usage()
      sys.exit(0)
    elif arg in ("-R","--RSA"):
      RAND_LEN = 8
      RAND_KEY = "r"
      FIXED_PT = True
    elif arg in ("-0","--RSANONZERO"):
      RAND_LEN = 8
      RAND_KEY = "R"
      FIXED_PT = True
    elif arg in ("-r","--samplerate"):
      SAMPLE_RATE = int(float(value))
    elif arg in ("-n","--samples"):
      NUM_SAMPLES = int(value);
    elif arg in ("-c","--count"):
      NUM_CAPTURES = int(value);
    elif arg in ("-o","--offset"):
      ANALOG_OFFSET = float(value)
    elif arg in ("-w","--write_file"):
      WRITE_FILE = value
  if WRITE_FILE is None and NUM_CAPTURES != 1:
    print "FATAL, you MUST specify an output file via -w"
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
    data = np.zeros((1,RAND_LEN),np.uint8)
    data_out = np.zeros((1,RAND_LEN),np.uint8)
    output_string = RAND_KEY + binascii.hexlify(os.urandom(RAND_LEN)) + "\n"
    traces[0,:],data_out[0,:] = encryptAndTrace_2CH(ps,output_string,0)
    data[0,:] = [0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff,0x00][0:RAND_LEN]
    # np.savez(sys.argv[2],traces=traces,data=data,data_out=data_out)
  else:
    traces = np.zeros((NUM_CAPTURES,NUM_SAMPLES),np.float32)
    data = np.zeros((NUM_CAPTURES,RAND_LEN),np.uint8)
    data_out = np.zeros((NUM_CAPTURES,RAND_LEN),np.uint8)
    for i in range(0,NUM_CAPTURES):
      if FIXED_PT:
        rand_input = "\xF0\xF0\xF0\xF0\x0F\x0F\x0F\x0F" # [0xF0,0xF0,0xF0,0xF0,0xF0,0xF0,0xF0,0xF0]
      else:
        rand_input = os.urandom(RAND_LEN)
      output_string = RAND_KEY + binascii.hexlify(rand_input) + "\n"
      time.sleep(0.1)
      # encryptAndTrace(ps,output_string)
      traces[i,:],data_out[i,:] = encryptAndTrace(ps,output_string,i)
      data[i,:] = [ord(x) for x in rand_input]
  ser.close()
  ps.stop()
  ps.close()
  print "Closing interfaces and saving, OK to unplug..."
  np.savez(WRITE_FILE,traces=traces,data=data,data_out=data_out,freq=[freq])
