#!/usr/bin/python

# Extremely simple signal plotting tool

import sys
import binascii
from scipy.signal import butter,lfilter,freqz
from numpy import *
import getopt
import matplotlib.pyplot as plt

def butter_lowpass(cutoff, fs, order=5):
  nyq = 0.5 * fs
  normal_cutoff = cutoff / nyq
  b, a = butter(order, normal_cutoff, btype='low', analog=False)
  return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
  b, a = butter_lowpass(cutoff, fs, order=order)
  y = lfilter(b, a, data)
  return y

OFFSET = 0
COUNT = 0
RULER = []

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"o:c:r:",["offset=","count=","ruler="])
  if(len(remainder) == 0):
    print "usage: ./plot.py [args] [file]"
    sys.exit(0)
  elif len(remainder) == 1:
    fn = remainder[0]
  else:
    print "usage: ./plot.py [args] [file]"
    sys.exit(0)
  for opt,arg in opts:
    if opt in ("-o","--offset"):
      OFFSET = int(float(arg))
    elif opt in ("-c","--count"):
      COUNT = int(float(arg))
    elif opt in ("-r","--ruler"):
      RULER.append(int(float(arg)))
    else:
      print "Unknown argument: %s" % opt
      sys.exit(0)
  dx = load(fn)
  d = dx['traces'][0]
  # f = open(fn)
  # dx = f.readlines()
  # d = [float32(x.rstrip().split(",")[0]) for x in dx[OFFSET:OFFSET + COUNT]]
  plt.plot(d)
  plt.title("Single Trace Plot")
  plt.ylabel("Power")
  plt.xlabel("Sample Count")
  plt.show()
