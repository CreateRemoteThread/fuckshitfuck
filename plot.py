#!/usr/bin/python

# Extremely simple signal plotting tool

import sys
import binascii
import random
from scipy.signal import butter,lfilter,freqz
from numpy import *
import time
import getopt
import matplotlib as mpl
import matplotlib.pyplot as plt

TRIGGERS = 0

lastTime = 0.0
lastX = 0

def onclick(event):
  global lastTime, lastX
  t = time.time()
  if t - lastTime < 0.200:
    print "debounce - nope"
    return
  elif event.xdata is None:
    print "skip - event.xdata (click on graph) is none"
    return
  else:
    lastTime = t
    if lastX == 0:
      lastX = int(event.xdata)
      print "MARK: %d" % lastX
    else:
      localX = int(event.xdata)
      fromX = min(lastX,localX)
      toX = max(lastX,localX)
      dist = toX - fromX
      print "FROM %d TO %d DIST %d" % (fromX,toX,dist)
      lastX = localX

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

SPECGRAM_EN = False
SPECGRAM_SR = 0

PLOT_SHOWN = False # dirty hack

TITLE = "Single Trace Plot"
XAXIS = "Sample Count"
YAXIS = "Power"

AVG_EN = False

def configure_average():
  global AVG_EN,TITLE
  AVG_EN = True
  TITLE = "Average Trace Plot"
  

def configure_fft(arg):
  global FFT_BASEFREQ,FFT_EN,TITLE,XAXIS
  FFT_BASEFREQ = float(arg)
  TITLE = "FFT Plot (%d Hz Sample Rate)" % FFT_BASEFREQ
  XAXIS = "Frequency"
  FFT_EN = True

def configure_specgram(arg):
  global SPECGRAM_EN, TITLE, XAXIS, YAXIS, SPECGRAM_SR
  TITLE = "Spectogram View"
  SPECGRAM_EN = True
  SPECGRAM_SR = float(arg)

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
  print " -l [cutoff,samplerate,order] : lowpass mode - units in hz"
  print " -F [samplerate] : plot fft, base freq in hz"
  print " -a : plot average trace"
  print " -s [samplerate] : plot spectrogram"

mpl.rcParams['agg.path.chunksize'] = 10000 


if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"s:ahl:n:o:c:r:f:F:",["spectrogram=","average","help","lowpass=","samples=","offset=","count=","ruler=","file=","fft="])
  for opt,arg in opts:
    if opt in ("-h","--help"):
      usage()
      sys.exit(0)
    elif opt in ("-s","--spectrogram"):
      configure_specgram(arg)
    elif opt in ("-a","--average"):
      configure_average()
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
  if [FFT_EN, LOWPASS_EN, AVG_EN, SPECGRAM_EN].count(True) > 1:
    print "You can only select one of -F (FFT), -l (LOWPASS) or -a (AVERAGE)"
    sys.exit(0)
  if SPECGRAM_EN == False:
    fig, ax1 = plt.subplots()
  for f in ADDITIONAL_FILES:
    df = load(f,mmap_mode = 'r')
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
      elif SPECGRAM_EN:
        fig, (ax1, ax2) = plt.subplots(nrows=2)
        ax1.set_title("Power Trace")
        ax1.set_ylabel("Power")
        ax1.set_xlabel("Sample Count")
        ax1.plot(d)
        ax2.set_title("Spectogram")
        ax2.set_ylabel("Frequency Component")
        ax2.set_xlabel("Time")
        ax2.specgram(d,NFFT=1024,Fs=SPECGRAM_SR,noverlap=900)
        fig.canvas.set_window_title("plot.py")
        plt.show()
        PLOT_SHOWN = True
      elif AVG_EN:
        if COUNT == 0:
          m = zeros(len(df['traces'][0]))
          numTraces = 0
          for trace in df['traces']:
            m[:] += trace[:]
            numTraces += 1
          m[:] /= numTraces
          plt.plot(m)
        else:
          m = zeros(COUNT)
          numTraces = 0
          for trace in df['traces']:
            m[:] += trace[OFFSET:OFFSET + COUNT]
            numTraces += 1
          m /= numTraces
          plt.plot(m)
      else:
        plt.plot(d)
  if PLOT_SHOWN is False:
    plt.title(TITLE)
    plt.ylabel(YAXIS)
    plt.xlabel(XAXIS)
    plt.grid()
    fig.canvas.mpl_connect("button_press_event",onclick)
    fig.canvas.set_window_title("plot.py")
    plt.show()
