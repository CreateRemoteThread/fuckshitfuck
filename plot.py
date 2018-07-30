#!/usr/bin/python

# Extremely simple signal plotting tool

import sys
import binascii
import random
from scipy.signal import butter,lfilter,freqz
from numpy import *
import getopt
import matplotlib.pyplot as plt

TRIGGERS = 0

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
NUM_TRACES = 1

ADDITIONAL_FILES = []

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"ls:o:c:r:a:",["lowpass","samples=","offset=","count=","ruler=","also="])
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
    elif opt in ("-s","--samples"):
      NUM_TRACES = int(arg)
    elif opt in ("-a","--also"):
      ADDITIONAL_FILES.append(arg)
    elif opt in ("-r","--ruler"):
      RULER.append(int(float(arg)))
    else:
      print "Unknown argument: %s" % opt
      sys.exit(0)
  dx = load(fn)
  for i in range(0,NUM_TRACES):
    if OFFSET == 0 and COUNT == 0:
      d = dx['traces'][i]
    else:
      d = dx['traces'][i][OFFSET:OFFSET + COUNT]
    plt.plot(d)
  for f in ADDITIONAL_FILES:
    df = load(f)
    if OFFSET == 0 and COUNT == 0:
      d = df['traces'][0]
    else:
      d = df['traces'][0][OFFSET:OFFSET + COUNT]
    plt.plot(d)
  plt.title("Single Trace Plot")
  plt.ylabel("Power")
  plt.xlabel("Sample Count")
  plt.show()
