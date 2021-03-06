#!/usr/bin/env python3

import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
from numpy import *
import getopt
import sys
import glob
import binascii
import support.filemanager

TRACE_OFFSET = 0
TRACE_LENGTH = 17000
TRACE_MAX = 0
sbox = [99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22]

CONFIG_PLOT = True

def butter_lowpass(cutoff, fs, order=5):
  nyq = 0.5 * fs
  normal_cutoff = cutoff / nyq
  b, a = butter(order, normal_cutoff, btype='low', analog=False)
  return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
  b, a = butter_lowpass(cutoff, fs, order=order)
  y = lfilter(b, a, data)
  return y

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
  dx = support.filemanager.load(fns)
  return (dx['traces'],dx['data'])

MAX_BYTES = 16

def deriveKey(data,plaintexts):
  global CONFIG_PLOT
  global TRACE_MAX
  bestguess = [0] * 16
  for bnum in range(0,MAX_BYTES):
    cpaoutput = [0]  * 256
    maxcpa = [0] * 256
    print(("Correlating hypotheses for byte %d" % bnum))
    for kguess in range(0,256):
      sumnum = np.zeros(TRACE_LENGTH)
      sumden1 = np.zeros(TRACE_LENGTH)
      sumden2 = np.zeros(TRACE_LENGTH)
      if TRACE_MAX == 0:
        trace_count = plaintexts[:,0].size
      else:
        trace_count = TRACE_MAX
      # print "round trace_count = %d" % trace_count
      hyp = zeros(trace_count)
      for tnum in range(0,trace_count):
        # hyp[tnum] = bin(plaintexts[tnum,bnum]  ^ kguess).count("1")
        hyp[tnum] = bin(sbox[plaintexts[tnum,bnum]  ^ kguess]).count("1")
      meanh = np.mean(hyp,dtype=np.float64)
      meant = np.mean(data,axis=0,dtype=np.float64)[TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH]
      # print meant
      # sys.exit(0)
      for tnum in range(0,trace_count):
        hdiff = (hyp[tnum] - meanh)
        tdiff = data[tnum,TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH] - meant
        sumnum = sumnum + (hdiff * tdiff)
        sumden1 = sumden1 + hdiff * hdiff
        sumden2 = sumden2 + tdiff * tdiff        
      cpaoutput[kguess] = sumnum / np.sqrt(sumden1 * sumden2)
      maxcpa[kguess] = max(abs(cpaoutput[kguess]))
    # print maxcpa
    # print maxcpa[np.argmax(maxcpa)]
    if CONFIG_PLOT:
      plt.plot(list(range(0,256)),maxcpa)
    bestguess[bnum] = np.argmax(maxcpa)
    sortedcpa = np.argsort(maxcpa)[::-1]
    print(("Selected: %02x; CPA: %f, %f, %f" % (bestguess[bnum], maxcpa[bestguess[bnum]], maxcpa[sortedcpa[1]],maxcpa[sortedcpa[2]])))
  return bestguess

fn = None

def usage():
  print(" cpa.py : part of the fuckshitfuck toolkit")
  print("----------------------------------------------")
  print(" -h : prints this message")
  print(" -o : offset to start correlating from")
  print(" -n : number of samples per trace")
  print(" -f : trace file (.npz from grab3.py)")
  print(" --txt : do not plot results (ssh mode)")

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"ho:n:f:c:",["help","offset=","samples=","file=","count=","txt"])
  for opt, arg in opts:
    if opt in ("-h","--help"):
      usage()
      sys.exit(0)
    elif opt in ("-o","--offset"):
      TRACE_OFFSET = int(arg)
    elif opt in ("-n","--samples"):
      TRACE_LENGTH = int(arg)
    elif opt in ("-c","--count"):
      TRACE_MAX = int(arg)
      print(("OVERRIDING trace_count to %d" % TRACE_MAX))
    elif opt == "--txt":
      CONFIG_PLOT = False
    elif opt in ("-f","--file"):
      fn = arg
  print(("TRACE_OFFSET = %d" % TRACE_OFFSET))
  print(("TRACE_LENGTH = %d" % TRACE_LENGTH))
  if fn is None:
    print("You must specify a file with -f")
    sys.exit(0)
  print("Stage 1: Loading plaintexts...")
  data,plaintexts = loadTraces(fn)
  print("Stage 2: Deriving key... wish me luck!")
  r = deriveKey(data,plaintexts)
  if CONFIG_PLOT:
    plt.title("AES SubKey Correlation Overview")
    plt.ylabel("Correlation")
    plt.xlabel("Hypothesis")
    plt.show()
  out = ""
  for i in range(0,16):
    out += "%02x " % int(r[i])
  print(("Done: %s" % out))
  out = ""
  actualKey = [0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c]
  out = ""
  for i in range(0,16):
    out += "%02x " % int(actualKey[i])
  print(("Done: %s" % out))
  out = ""
