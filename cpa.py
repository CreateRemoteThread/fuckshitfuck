#!/usr/bin/python

import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
from numpy import *
import sys
import glob
import binascii

TRACE_OFFSET = 0
TRACE_LENGTH = 50000
sbox = [99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22]

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
  data = zeros((TRACE_LENGTH,len(fns)),float32)
  plaintexts = zeros((16,len(fns)),uint8)
  for fn_c in range(0,len(fns)):
    fn = fns[fn_c]
    plaintext = binascii.unhexlify(fn[-36:-4])
    f = open(fn,"r")
    dx = f.readlines()[TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH]
    d = [np.float32(x.rstrip().split(",")[0]) for x in dx]
    f.close()
    data[:,fn_c] = d
    # data[:,fn_c] = butter_lowpass_filter(d,10000,40e6,3)
    plaintexts[:,fn_c] = [uint8(ord(i)) for i in plaintext]
  print "Loaded %d trace pairs" % len(fns)
  print "Plaintext size: %d" % plaintexts[:,0].size
  print "Trace size: %d" % data[:,0].size
  # print "Loaded %d data, %d plaintexts" % (data[:,0].size,plaintexts[:,0].size)
  return (data,plaintexts)

# print plaintexts[:,0]
def deriveKey(data,plaintexts):
  bestguess = [0] * 16
  for bnum in range(0,16):
    cpaoutput = [0]  * 256
    maxcpa = [0] * 256
    print "Correlating hypotheses for byte %d" % bnum
    for kguess in range(0,256):
      sumnum = np.zeros(TRACE_LENGTH)
      sumden1 = np.zeros(TRACE_LENGTH)
      sumden2 = np.zeros(TRACE_LENGTH)
      hyp = zeros(plaintexts[0,:].size)
      for tnum in range(0,plaintexts[0,:].size):
        hyp[tnum] = bin(sbox[plaintexts[bnum,tnum]  ^ kguess]).count("1")
      meanh = np.mean(hyp,dtype=np.float64)
      meant = np.mean(data,axis=1,dtype=np.float64)
      # print meant
      # sys.exit(0)
      for tnum in range(0,200):
        hdiff = (hyp[tnum] - meanh)
        tdiff = data[:,tnum] - meant
        sumnum = sumnum + (hdiff * tdiff)
        sumden1 = sumden1 + hdiff * hdiff
        sumden2 = sumden2 + tdiff * tdiff        
      cpaoutput[kguess] = sumnum / np.sqrt(sumden1 * sumden2)
      maxcpa[kguess] = max(abs(cpaoutput[kguess]))
    # print maxcpa
    # print maxcpa[np.argmax(maxcpa)]
    plt.plot(range(0,256),maxcpa)
    bestguess[bnum] = np.argmax(maxcpa)
  return bestguess

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "usage: ./cpa.py [traceset1] [traceset2]"
    sys.exit(0)
  fns = []
  for s in sys.argv[1:]:
    fns += glob.glob("%s/*.csv" % s)
  print "Stage 2: Loading plaintexts..."
  data,plaintexts = loadTraces(fns)
  print "Stage 3: Deriving key... wish me luck!"
  r = deriveKey(data,plaintexts)
  print "Done: Recovered key %s" % ["%02x" % rx for rx in r]
  plt.title("AES SubKey Correlation Overview")
  plt.ylabel("Correlation")
  plt.xlabel("Hypothesis")
  plt.show()
