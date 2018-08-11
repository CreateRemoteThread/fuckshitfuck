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

LOWPASS_CUTOFF = 10000
LOWPASS_SR = 40000000
LOWPASS_ORDER = 5
LOWPASS_EN = False

FFT_BASEFREQ = 40000000
FFT_EN = False

TITLE = "Single Plot Trace"
XAXIS = "Sample Count"
YAXIS = "Power"

def configure_fft(arg):
  global FFT_BASEFREQ,FFT_EN,TITLE
  FFT_BASEFREQ = float(arg)
  TITLE = "FFT Plot (%d Hz Sample Rate)" % FFT_BASEFREQ
  XAXIS = "Frequency"
  FFT_EN = True

def configure_lowpass(in_str):
  global LOWPASS_CUTOFF, LOWPASS_SR, LOWPASS_ORDER, LOWPASS_EN, TITLE
  try:
    (cutoff,samplerate,order) = in_str.split(",")
  except:
    print "syntax: -l 10000,40000000,5 (cutoff, samplerate, order)"
    sys.exit(0)
  LOWPASS_CUTOFF = float(cutoff)
  LOWPASS_SR = float(samplerate)
  LOWPASS_ORDER = int(order)
  LOWPASS_EN = True
  TITLE = "Low Pass (%d Hz SR, %d Hz Cutoff)" % (LOWPASS_SR,LOWPASS_CUTOFF)

def usage():
  print " plot.py : part of the fuckshitfuck toolkit"
  print "----------------------------------------------"
  print " -h : prints this message"
  print " -o : offset to start plotting samples from"
  print " -n : number of samples from offset to plot"
  print " -c : number of traces to plot"
  print " -f : input npz file (can be multiple)"
  print " -r : print vertical ruler at point (NOT IMPLEMENTED)"
  print " -l [cutoff,freq,order] : lowpass mode - units in hz"
  print " -F [freq] : plot fft, base freq in hz"

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"hl:n:o:c:r:f:F:",["help","lowpass=","samples=","offset=","count=","ruler=","file=","fft="])
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
    elif opt in ("-l","--lowpass"):
      configure_lowpass(arg)
    elif opt in ("-F","--fft"):
      configure_fft(arg)
    elif opt in ("-r","--ruler"):
      RULER.append(int(float(arg)))
    else:
      print "Unknown argument: %s" % opt
      sys.exit(0) 
  if FFT_EN and LOWPASS_EN:
    print "Combining an FFT and a Low Pass is unsupported"
    sys.exit(0)
  for f in ADDITIONAL_FILES:
    df = load(f)
    for i in range(0,NUM_TRACES):
      if OFFSET == 0 and COUNT == 0:
        d = df['traces'][0]
      else:
        d = df['traces'][0][OFFSET:OFFSET + COUNT]
      if LOWPASS_EN:
        plt.plot(butter_lowpass_filter(d,LOWPASS_CUTOFF,LOWPASS_SR,LOWPASS_ORDER))
      elif FFT_EN:
        n = len(d)
        k = arange(n)
        T = n / FFT_BASEFREQ
        frq = k / T
        frq = frq[range(n/2)]
        Y = fft.fft(d)/n
        Y = Y[range(n/2)]
        plt.plot(frq,abs(Y),'r') 
      else:
        plt.plot(d)
  plt.title(TITLE)
  plt.ylabel(YAXIS)
  plt.xlabel(XAXIS)
  plt.grid()
  plt.show()
