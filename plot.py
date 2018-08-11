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
GAIN_FACTOR =  31622.0
ADDITIONAL_FILES = []

def usage():
  print " plot.py : part of the fuckshitfuck toolkit"
  print "----------------------------------------------"
  print " -h : prints this message"
  print " -o : offset to start plotting samples from"
  print " -n : number of samples from offset to plot"
  print " -c : number of traces to plot"
  print " -f : input npz file (can be multiple)"
  print " -r : print vertical ruler at point (NOT IMPLEMENTED)"
  print " -l : do soft low pass filter (NOT IMPLEMENTED)"

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"hln:o:c:r:f:",["help","lowpass","samples=","offset=","count=","ruler=","file="])
  for opt,arg in opts:
    if opt in ("-h","--help"):
      usage()
      sys.exit(0)
    elif opt in ("-o","--offset"):
      OFFSET = int(float(arg))
    elif opt in ("-n","--samples"):
      COUNT = int(float(arg))
    elif opt in ("-c","--count"):
      NUM_TRACES = int(arg)
    elif opt in ("-f","--file"):
      ADDITIONAL_FILES.append(arg)
    elif opt in ("-r","--ruler"):
      RULER.append(int(float(arg)))
    else:
      print "Unknown argument: %s" % opt
      sys.exit(0) 
  for f in ADDITIONAL_FILES:
    df = load(f)
    for i in range(0,NUM_TRACES):
      if OFFSET == 0 and COUNT == 0:
        d = df['traces'][0]
      else:
        d = df['traces'][0][OFFSET:OFFSET + COUNT]
      plt.plot(d)
  plt.title("Single Trace Plot")
  plt.ylabel("Power")
  plt.xlabel("Sample Count")
  plt.grid()
  plt.show()
