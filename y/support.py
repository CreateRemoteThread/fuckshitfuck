#!/usr/bin/env python3

import numpy as np
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import getopt
import glob

CONFIG_PEAK_IDENTIFY = 0.2
CONFIG_MAX_PULSEWIDTH = 40000

def specialk(val):
  if val < 0.02:
    return 0.0
  else:
    return val

def findLocalMaxima(data):
  localMaxima = []
  i = 0
  while i < len(data):
    if data[i] >= CONFIG_PEAK_IDENTIFY:
      if i + CONFIG_MAX_PULSEWIDTH > len(data):
        print("findLocalMaxima(): ending peak detection")
        break
      localMaxima.append(i)
      i += 1000
    i += 1
  return localMaxima

def twoOfThree(unknown,alignment):
  lm = findLocalMaxima(unknown)
  maxCorr = {}
  for local_max in lm:
    data = unknown[local_max:local_max+CONFIG_MAX_PULSEWIDTH]
    data = list(map(specialk,abs(data)))
    for k in alignment.keys():
      (alignData,alignMaxima) = alignment[k]
      for align_max in alignMaxima:
        align_slice = alignData[align_max:align_max+CONFIG_MAX_PULSEWIDTH]
        align_slice = list(map(specialk,abs(align_slice)))
        # print("Matching: %d %d" % (len(data),len(align_slice)))
        lcorr = np.corrcoef(data,align_slice)[0,1]
        # if lcorr > 0.8:
        #   print("Strong match on %s: %f" % (k,lcorr))
        # else:
        #   print("Poor match on %s: %f" % (k,lcorr))
        if k in maxCorr.keys():
          maxCorr[k] += lcorr
        else:
          maxCorr[k] = lcorr
  maxCorrCoef = 0
  maxKey = ""
  for k in maxCorr.keys():
    # print("Combined 2of3 correlation for %s is %f" % (k,maxCorr[k]))
    if maxCorr[k] > maxCorrCoef:
      maxCorrCoef = maxCorr[k]
      maxKey = k
  # print("I think the key is %s" % maxKey)
  return (maxKey,maxCorr)

CONFIG_FILENAME = None
CONFIG_THEATRICAL = False

def usage():
  print("lol")
  sys.exit(0)

if __name__ == "__main__":
  print("support.py post-processing tool")
  optlist,args = getopt.getopt(sys.argv[1:],"hf:a",["help","all","file=","theatre"])
  for opt, arg in optlist:
    if opt in ("-h","--help"):
      usage()
    elif opt in ("-f","--file"):
      CONFIG_FILENAME = arg
    elif opt in ("-a","--all"):
      CONFIG_FILENAME = None
    elif opt in ("-theatre"):
      CONFIG_THEATRICAL = True
  print("stage 1: preloading keystroke alignment data")
  alignment = {}
  # flist = list(glob.glob("toothpicks/*.npy"))
  # flist.sort()
  for f in glob.glob("toothpicks/*.npy"):
    fname = f.replace("toothpicks/","")
    fname = fname.replace(".npy","")
    fx = np.load(f)
    localMaxima = findLocalMaxima(fx)
    alignment[fname] = (fx,localMaxima)
    print("+ Loaded alignment table for %s" % fname)
  if CONFIG_FILENAME is None:
    flist = glob.glob("floss/*.npy")
    flist.sort()
    for f in flist:
      data = np.load(f)
      (s,maxCorr) = twoOfThree(data,alignment)
      print("I think %s is %s" % (f,s))
  else:
    data = np.load(CONFIG_FILENAME)
    (k,maxCorr) = twoOfThree(data,alignment)
    print("I think %s is %s" % (CONFIG_FILENAME,k))
