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

TRACE_OFFSET = 120000
TRACE_LENGTH = 50000

def loadTraces(fns):
  dx = np.load(fns,"r")
  return (dx['traces'],dx['data'])

MAX_BYTES = 16

def deriveKey(data,plaintexts):
  desManager = {}
  bestguess = [0] * 16
  cpaoutput = [0]  * 48
  maxcpa = [0] * 48
  for kguess in range(0,48):
    sumnum = np.zeros(TRACE_LENGTH)
    sumden1 = np.zeros(TRACE_LENGTH)
    sumden2 = np.zeros(TRACE_LENGTH)
    hyp = zeros(plaintexts[:,0].size)
    for tnum in range(0,plaintexts[:,0].size):
      if tnum not in desManager.keys():
        desManager[tnum] = desIntermediateValue()
        desManager[tnum].preprocess(plaintexts[tnum])
      hyp[tnum] = bin(desManager[tnum].generateSbox(1,kguess)).count("1")
    meanh = np.mean(hyp,dtype=np.float64)
    meant = np.mean(data,axis=0,dtype=np.float64)[TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH]
    for tnum in range(0,len(plaintexts)):
      hdiff = (hyp[tnum] - meanh)
      tdiff = data[tnum,TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH] - meant
      sumnum = sumnum + (hdiff * tdiff)
      sumden1 = sumden1 + hdiff * hdiff
      sumden2 = sumden2 + tdiff * tdiff        
    cpaoutput[kguess] = sumnum / np.sqrt(sumden1 * sumden2)
    maxcpa[kguess] = max(abs(cpaoutput[kguess]))
    print "For guess %02x, our correlation is %f" % (kguess,maxcpa[kguess])
    bestguess[0] = np.argmax(maxcpa)
    sortedcpa = np.argsort(maxcpa)[::-1]
  plt.plot(range(0,48),maxcpa)
  print "Selected: %02x" % bestguess[0]
  return bestguess

fn = None

def usage():
  print " cpa.py : part of the fuckshitfuck toolkit"
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
  print "Stage 2: Deriving SUBKEY 0 ONLY!"
  r = deriveKey(data,plaintexts)
  plt.title("DES SubKey Overview")
  plt.ylabel("Correlation")
  plt.xlabel("Hypothesis")
  plt.show()
