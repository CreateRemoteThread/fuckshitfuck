#!/usr/bin/python

import sys
import binascii
from scipy.signal import butter,lfilter,freqz
from numpy import *
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

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "usage: ./plot-test.py [trace]"
    sys.exit(0)
  f = open(sys.argv[1])
  dx = f.readlines()[0:50000]
  d = [float32(x.rstrip().split(",")[0]) for x in dx]
  plaintext = binascii.unhexlify(sys.argv[1][-36:-4])
  plt.plot(d)
  plt.ylabel("lol")
  plt.show()
