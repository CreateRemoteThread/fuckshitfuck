#!/usr/bin/python

import numpy as np
from numpy import *
import sys
import glob
import getopt
import matplotlib.pyplot as plt
import binascii
from dessupport import desIntermediateValue

TRACE_OFFSET = 0
TRACE_LENGTH = 2000

def loadTraces(fns):
  dx = np.load(fns,"r")
  return (dx['traces'],dx['data'])

def deriveKey(data,plaintexts):
  global TRACE_OFFSET
  recovered = zeros(8)
  desManager = {}
  for BYTE_POSN in range(0,8):
    TRACE_OFFSET = BYTE_POSN * 1975
    print "Attempting recovery of byte %d..." % BYTE_POSN
    plfh = zeros(48)
    for KEY_GUESS in range(0,48):
      numGroup1 = 0
      numGroup2 = 0
      group1 = zeros(TRACE_LENGTH)
      group2 = zeros(TRACE_LENGTH)
      diffProfile = zeros(TRACE_LENGTH)
      for TRACE_NUM in range(0,data[:,0].size):
        if TRACE_NUM not in desManager.keys():
          desManager[TRACE_NUM] = desIntermediateValue()
          desManager[TRACE_NUM].preprocess(plaintexts[TRACE_NUM])
        hypothesis = desManager[TRACE_NUM].generateSbox(BYTE_POSN,KEY_GUESS) 
        if bin(hypothesis).count("1") > 2:
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
    plt.plot(range(0,48),plfh)
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
  plt.title("DES Power Leakage v Hypothesis Overview")
  plt.ylabel("Maximum Diff. of Means")
  plt.xlabel("Key Hypothesis")
  plt.show()
  out = ""
  for i in range(0,8):
    out += "%02x " % int(r[i])
  print "Done: %s" % out

