#!/usr/bin/python

import numpy as np
from numpy import *
import sys
import glob
import getopt
import matplotlib.pyplot as plt
import binascii
import support.filemanager
import support.attack

TRACE_OFFSET = 0
TRACE_LENGTH = 17000
TRACE_MAX = 0

CONFIG_PLOT = True
CONFIG_LEAKMODEL = "helpmsg"

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

def deriveKey(data,plaintexts):
  global TRACE_MAX
  leakmodel = support.attack.fetchModel(CONFIG_LEAKMODEL)
  leakmodel.loadPlaintextArray(plaintexts) 
  recovered = zeros(leakmodel.keyLength)
  for BYTE_POSN in range(0,leakmodel.keyLength):
    print("Attempting recovery of byte %d..." % BYTE_POSN)
    plfh = zeros(leakmodel.fragmentMax)
    for KEY_GUESS in range(0,leakmodel.fragmentMax):
      numGroup1 = 0
      numGroup2 = 0
      group1 = zeros(TRACE_LENGTH)
      group2 = zeros(TRACE_LENGTH)
      diffProfile = zeros(TRACE_LENGTH)
      if TRACE_MAX == 0:
        trace_count = data[:,0].size
      else:
        trace_count = TRACE_MAX
      for TRACE_NUM in range(0,trace_count):
        # hyp = sbox[plaintexts[TRACE_NUM,BYTE_POSN] ^ KEY_GUESS]
        hypothesis = leakmodel.genIValRaw(TRACE_NUM,BYTE_POSN,KEY_GUESS) # sbox[plaintexts[TRACE_NUM,BYTE_POSN] ^ KEY_GUESS]
        # if hyp != hypothesis:
        #   print("Fatal, hypothesis calculation wrong")
        #   sys.exit(0)
        if bin(hypothesis)[2:][-1] == "1":
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
    print("Selected %02x, %f, %f, %f" % (argmax(plfh),plfh[sorted_dpa[0]],plfh[sorted_dpa[1]],plfh[sorted_dpa[2]]))
    if CONFIG_PLOT:
      plt.plot(list(range(0,leakmodel.fragmentMax)),plfh)
    recovered[BYTE_POSN] = argmax(plfh)
  return recovered

fn = None

def usage():
  print(" dpa.py : part of the fuckshitfuck toolkit")
  print("----------------------------------------------")
  print(" -h : prints this message")
  print(" -o : offset to start correlating from")
  print(" -n : number of samples per trace")
  print(" -f : trace file (.npz from grab3.py)")
  print(" -a : specify algo + leakage model")
  print(" --txt : do not plot (ssh mode)")

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"ho:n:f:c:a:",["help","offset=","samples=","file=","count=","algo=","txt"])
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
    elif opt in ("-f","--file"):
      fn = arg
    elif opt in ("-a","--algo"):
      CONFIG_LEAKMODEL = arg
    elif opt == "--txt":
      CONFIG_PLOT = False
  print("TRACE_OFFSET = %d" % TRACE_OFFSET)
  print("TRACE_LENGTH = %d" % TRACE_LENGTH)
  if fn is None:
    print("You must specify a file with -f")
    sys.exit(0)
  print("Stage 1: Loading plaintexts...")
  data,plaintexts = loadTraces(fn)
  print("Deriving key... wish me luck!")
  r = deriveKey(data,plaintexts)
  if CONFIG_PLOT:
    plt.title("AES Power Leakage v Hypothesis Overview")
    plt.ylabel("Maximum Diff. of Means")
    plt.xlabel("Key Hypothesis")
    plt.show()
  out = ""
  for i in range(0,16):
    out += "%02x " % int(r[i])
  print("Done: %s" % out)
  out = ""
  out = ""

