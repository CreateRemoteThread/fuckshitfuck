#!/usr/bin/env python3

import matplotlib as mpl
# mpl.use("Agg")
import matplotlib.pyplot as plt
import scipy.io
from scipy.signal import butter,lfilter, freqz
import numpy as np
import sys
import support

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
  if len(sys.argv) < 2:
    print("usage: ./plotlite.py <savegame>")
    sys.exit(0)
  data = np.load(sys.argv[1])
  if len(data) == 2:
    plt.subplot(2,1,1)
    plt.title("Channel A - %s" % (sys.argv[1]))
    data0_slice = data[0][0:75000]
    # from scipy import signal
    # f,Pxx_spec = signal.welch(data0_slice,124999999,'flattop',1024,scaling='spectrum')
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Linear Spectrum")
    # plt.semilogy(f,np.sqrt(Pxx_spec))
    plt.plot(support.block_preprocess_function(data0_slice))
    # plt.plot(abs(data[0]))
    plt.subplot(2,1,2)
    plt.title("Channel B")
    data1_slice = data[1][0:75000]
    # f2,Pxx_spec2 = signal.welch(data1_slice,124999999,'flattop',1024,scaling='spectrum')
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Linear Spectrum")
    plt.plot(support.block_preprocess_function(data1_slice))
    # plt.semilogy(f2,np.sqrt(Pxx_spec2))
    #plt.plot(abs(data[1]))
    plt.show()
  else:
    plt.title("Channel A")
    plt.plot(data)
    plt.show()
  
