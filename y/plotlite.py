#!/usr/bin/env python3

import matplotlib as mpl
# mpl.use("Agg")
import matplotlib.pyplot as plt
import scipy.io
from scipy.signal import butter,lfilter, freqz
import numpy as np
import sys

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
    print("usage: ./plotlite.py <savegame>")
    sys.exit(0)
  data = np.load(sys.argv[1])
  # d_filtered = butter_lowpass_filter(data,60000,60000000,1)
  plt.plot(abs(data))
  plt.show()
  # plt.savefig("lol.png")
  
