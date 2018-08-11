#!/usr/bin/python

import numpy as np
from numpy import *
import sys
import glob
import getopt
import matplotlib.pyplot as plt
import binascii

TRACE_OFFSET = 0
TRACE_LENGTH = 17000

sbox = [99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22]

def getUsefulTraceLength(fn):
  f = open(fn)
  c = 0
  for l_ in f.readlines():
    (data,size) = l_.rstrip().split(",")
    if np.float32(size) > 0.5:
      c += 1
    else:
      break
  f.close()
  return c

def loadTraces(fns):
  dx = np.load(fns,"r")
  return (dx['traces'],dx['data'])

# def loadTraces(fns):
#   data = zeros((TRACE_LENGTH,len(fns)),float32)
#   plaintexts = zeros((16,len(fns)),uint8)
#   for fn_c in range(0,len(fns)):
#     fn = fns[fn_c]
#     plaintext = binascii.unhexlify(fn[-36:-4])
#     f = open(fn,"r")
#     dx = f.readlines()[TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH]
#     d = [np.float32(x.rstrip().split(",")[0]) for x in dx]
#     f.close()
#     data[:,fn_c] = d
#     # data[:,fn_c] = butter_lowpass_filter(d,10000,40e6,3)
#     plaintexts[:,fn_c] = [uint8(ord(i)) for i in plaintext]
#   print "Loaded %d trace pairs" % len(fns)
#   print "Plaintext size: %d" % plaintexts[:,0].size
#   print "Trace size: %d" % data[:,0].size
#   # print "Loaded %d data, %d plaintexts" % (data[:,0].size,plaintexts[:,0].size)
#   return (data,plaintexts)

def deriveKey(data,plaintexts):
  recovered = zeros(16)
  for BYTE_POSN in range(0,16):
    print "Attempting recovery of byte %d..." % BYTE_POSN
    plfh = zeros(256)
    for KEY_GUESS in range(0,256):
      numGroup1 = 0
      numGroup2 = 0
      group1 = zeros(TRACE_LENGTH)
      group2 = zeros(TRACE_LENGTH)
      diffProfile = zeros(TRACE_LENGTH)
      for TRACE_NUM in range(0,data[:,0].size):
        hypothesis = sbox[plaintexts[TRACE_NUM,BYTE_POSN] ^ KEY_GUESS]
        # if hypothesis % 2 == 1:
        if hypothesis % 2 == 1:
          group1[:] += data[TRACE_NUM,TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH]
          numGroup1 += 1
        else:
          group2[:] += data[TRACE_NUM,TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH]
          numGroup2 += 1
      group1[:] /= numGroup1
      group2[:] /= numGroup2
      diffProfile = abs(group1[:] - group2[:])
      plfh[KEY_GUESS] = max(diffProfile)
    sorted_dpa = argsort(plfh)[::-1]
    print "Selected %02x, %f, %f, %f" % (argmax(plfh),plfh[sorted_dpa[0]],plfh[sorted_dpa[1]],plfh[sorted_dpa[2]])
    plt.plot(range(0,256),plfh)
    recovered[BYTE_POSN] = argmax(plfh)
  return recovered

fn = None

def usage():
  print " dpa.py : part of the fuckshitfuck toolkit"
  print "----------------------------------------------"
  print " -h : prints this message"
  print " -o : offset to start correlating from"
  print " -n : number of samples per trace"
  print " -f : trace file (.npz from grab3.py)"

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"ho:n:f:",["help","offset=","samples=","file="])
  for opt, arg in opts:
    if opt in ("-h","--help"):
      usage()
      sys.exit(0)
    elif opt in ("-o","--offset"):
      TRACE_OFFSET = int(arg)
    elif opt in ("-n","--samples"):
      TRACE_LENGTH = int(arg)
    elif opt in ("-f","--file"):
      fn = arg
  print "TRACE_OFFSET = %d" % TRACE_OFFSET
  print "TRACE_LENGTH = %d" % TRACE_LENGTH
  if fn is None:
    print "You must specify a file with -f"
    sys.exit(0)
  print "Stage 1: Loading plaintexts..."
  data,plaintexts = loadTraces(fn)
  print "Deriving key... wish me luck!"
  r = deriveKey(data,plaintexts)
  plt.title("AES Power Leakage v Hypothesis Overview")
  plt.ylabel("Maximum Diff. of Means")
  plt.xlabel("Key Hypothesis")
  plt.show()
  out = ""
  for i in range(0,16):
    out += "%02x " % int(r[i])
  print "Done: %s" % out
  out = ""
  actualKey = [0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c]
  out = ""
  for i in range(0,16):
    out += "%02x " % int(actualKey[i])
  print "Done: %s" % out
  out = ""

