#!/usr/bin/python

import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
from numpy import *
import getopt
import sys
import glob
import binascii
from dessupport import desIntermediateValue
import support.filemanager

TRACE_OFFSET = 0
TRACE_LENGTH = 0
TRACE_MAX = 0

def loadTraces(fns):
  dx = support.filemanager.load(fns)
  return (dx['traces'],dx['data'])

MAX_BYTES = 8

CONFIG_PLOT = True

def deriveKey(data,plaintexts):
  global CONFIG_PLOT
  global TRACE_MAX
  bestguess = [0] * 8
  desManager = {}
  for bnum in range(0,MAX_BYTES):
    cpaoutput = [0]  * 64
    maxcpa = [0] * 64
    print("Correlating hypotheses for byte %d" % bnum)
    for kguess in range(0,64):
      sumnum = np.zeros(TRACE_LENGTH)
      sumden1 = np.zeros(TRACE_LENGTH)
      sumden2 = np.zeros(TRACE_LENGTH)
      if TRACE_MAX == 0:
        trace_count = plaintexts[:,0].size
      else:
        trace_count = TRACE_MAX
      hyp = zeros(trace_count)
      for tnum in range(0,trace_count):
        if tnum not in list(desManager.keys()):
          desManager[tnum] = desIntermediateValue()
          desManager[tnum].preprocess(plaintexts[tnum])
        hyp[tnum] = bin(desManager[tnum].generateSbox(bnum,kguess)).count("1")
      meanh = np.mean(hyp,dtype=np.float64)
      meant = np.mean(data,axis=0,dtype=np.float64)[TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH]
      for tnum in range(0,trace_count):
        hdiff = (hyp[tnum] - meanh)
        tdiff = data[tnum,TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH] - meant
        sumnum = sumnum + (hdiff * tdiff)
        sumden1 = sumden1 + hdiff * hdiff
        sumden2 = sumden2 + tdiff * tdiff
      d_ = np.sqrt(sumden1 * sumden2)
      d = np.zeros(len(d_))
      for d_index in range(0,len(d_)):
        if d_[d_index] == 0.0:
          d[d_index] = 1.0
        else:
          d[d_index] = d_[d_index]
      cpaoutput[kguess] = sumnum / d
      maxcpa[kguess] = max(abs(cpaoutput[kguess]))
    if CONFIG_PLOT:
      plt.plot(list(range(0,64)),maxcpa)
    bestguess[bnum] = np.argmax(maxcpa)
    sortedcpa = np.argsort(maxcpa)[::-1]
    print("Selected: %02x; CPA: %f, %f, %f" % (bestguess[bnum], maxcpa[bestguess[bnum]], maxcpa[sortedcpa[1]],maxcpa[sortedcpa[2]]))
    for tnum_cumulative in range(0,plaintexts[:,0].size):
      desManager[tnum_cumulative].saveCumulative(bnum,bestguess[bnum])
      desManager[tnum_cumulative].disableCumulative = True
  return bestguess

fn = None

def usage():
  print(" cpa.py : part of the fuckshitfuck toolkit")
  print("----------------------------------------------")
  print(" -h : prints this message")
  print(" -o : offset to start correlating from")
  print(" -n : number of samples per trace")
  print(" -f : trace file (.npz from grab3.py)")
  print(" --txt : do not plot (ssh mode)")

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
    elif opt == "--txt":
      CONFIG_PLOT = False
    elif opt in ("-f","--file"):
      fn = arg
  print("TRACE_OFFSET = %d" % TRACE_OFFSET)
  print("TRACE_LENGTH = %d" % TRACE_LENGTH)
  if fn is None:
    print("You must specify a file with -f")
    sys.exit(0)
  print("Stage 1: Loading plaintexts...")
  data,plaintexts = loadTraces(fn)
  if TRACE_LENGTH == 0:
    TRACE_LENGTH = len(data[0])
    print("Setting trace length to %d" % TRACE_LENGTH)
  print("Stage 2: Deriving key... wish me luck!")
  r = deriveKey(data,plaintexts)
  if CONFIG_PLOT:
    plt.title("DES SubKey Correlation Overview")
    plt.ylabel("Correlation")
    plt.xlabel("Hypothesis")
    plt.show()
  out = ""
  for i in range(0,8):
    out += "%02x " % int(r[i])
  print("Done: %s" % out)
  out = ""
