#!/usr/bin/env python3

import numpy as np
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SND_NORMAL_WAIT = 60000
SND_NORMAL_ACTIVE = 20000
SND_ERROR_MARGIN = 10000

SND_STATE_WAITFIRST = 0
SND_STATE_ACTIVE = 1

def slice_and_dice(local_a):
  state = SND_STATE_WAITFIRST
  i = 0
  static_len_a = len(local_a)
  lastIndex = 0
  signal = []
  signalSuffix = []
  while i < static_len_a:
    (index,maxima) = local_a[i]
    lastGap = index - lastIndex
    if state == SND_STATE_WAITFIRST:
      if abs(lastGap - SND_NORMAL_WAIT) <= SND_ERROR_MARGIN:
        signal.append(1)
        state = SND_STATE_ACTIVE
      elif abs(lastGap - (SND_NORMAL_WAIT + SND_NORMAL_ACTIVE)) <= SND_ERROR_MARGIN:
        state = SND_STATE_ACTIVE
        signal.append(0,1)
        # this could be on the other end. use a calibration waveform.
      elif abs(lastGap - (SND_NORMAL_WAIT + SND_NORMAL_ACTIVE * 2)) <= SND_ERROR_MARGIN:
        state = SND_STATE_ACTIVE
        signal.append(0,1)
        signalSuffix = [0]
      else:
        pass
    elif state == SND_STATE_ACTIVE:
      if len(signal) == 18:
        print("OK, stopping at signal %d" % i)
        return signal + signalSuffix
      if abs(lastGap - SND_NORMAL_ACTIVE) <= SND_ERROR_MARGIN:
        signal.append(1)
      else:
        gap = abs(lastGap - SND_NORMAL_ACTIVE) - SND_NORMAL_ACTIVE
        fullZeroes = int(gap / SND_NORMAL_ACTIVE)
        if gap/SND_NORMAL_ACTIVE > 0.5:
          fullZeroes += 1
        for lol in range(0,fullZeroes):
          signal.append(0)
    i += 1
    # print("Processing sample %d" % i)
    lastIndex = index
  if len(signal) != 18:
    print("Bad sample, discard this")
    return []

def snd2(local_a):
  static_len_a = len(local_a)
  i = 0
  lastIndex = 0
  while i < static_len_a:
    (index,local_maxima) = local_a[i]
    if abs((index - lastIndex) - SND_NORMAL_WAIT) < SND_ERROR_MARGIN:
      return local_a[i:i+18]
    i += 1
    lastIndex = index
  print("Bad sample, discard this")
  return []  
     
LOCAL_MAXIMA_WINDOW = 500
LOCAL_MAXIMA_BACKOFF = 1000
def find_local_maxima(trace_raw):
  trace = list(map(abs,trace_raw))
  firstPeak = 0
  static_len_data = len(trace)
  for i in range(0,static_len_data):
    if trace[i] > 0.15:
      firstPeak = i
      break
  peak_finder = []
  i = 0
  while i < static_len_data:
    if trace[i] > 0.15:
      local_maxima = max(trace[i:i+LOCAL_MAXIMA_WINDOW])
      peak_finder.append( (i,local_maxima) )
      i += LOCAL_MAXIMA_BACKOFF
    else:
      i += 1
  return peak_finder

def map_delay(local_a):
  static_len_a = len(local_a)
  indexes = []
  localIndex = 0
  for i in range(0,static_len_a):
    (index,maxima) = local_a[i]
    if localIndex == 0:
      indexes.append(0)
    else:
      # if index - localIndex > 11000:
      #   print("Adjusting index by 4000: %d" % (index - localIndex))
      #   indexes.append((index - localIndex) - 4000)
      # else:
      #   indexes.append(index - localIndex)
      indexes.append(index - localIndex)
    localIndex = index
  return indexes

def test_discard_usb():
  d = open("fuck.log")
  for l_ in d.readlines():
    l = l_.rstrip()
    data = eval(l)
    bucket_normal = []
    bucket_spike = []
    # first pass: work out the mean for each half.
    for i in range(1,len(data)):
      if abs(data[i] - 10000) < 500:
        bucket_normal.append(data[i])
      else:
        bucket_spike.append(data[i])
    avg_normal = min(bucket_normal)
    avg_spike = min(bucket_spike)
    # normalize
    bucket_processed = []
    for i in range(1,len(data)):
      if abs(data[i] - 10000) < 500:
        bucket_processed.append( int(data[i] - avg_normal) )
      else:
        bucket_processed.append( int(data[i] - avg_spike) )
    print("AVGNML: %d AVGSPK: %d BUCKET: %s" % (int(avg_normal), int(avg_spike), str(bucket_processed)) )

lastIndex = 0
if __name__ == "__main__":
  if len(sys.argv) == 2:
    if sys.argv[1] == "normalize":
      test_discard_usb()
      sys.exit(0)
    data = np.load(sys.argv[1])
    lm = find_local_maxima(data)
    d2 = snd2(lm)
    # (index,maxima) = d2[0]
    plt.clf()
    plt.plot(data)
    for (index,maxima) in d2:
      plt.axvline(x=index,c='red')
    plt.savefig("images/raw.png")
    print(map_delay(d2))
    sys.exit(0)
  else:
    import glob
    i = 0
    for x in glob.glob("saves/*.npy"):
      data = np.load(x)
      lm = find_local_maxima(data)
      d2 = snd2(lm)
      xy = map_delay(d2)
      print(xy)
      plt.clf()
      plt.plot(xy)
      plt.savefig("images/%d.png" % i)
      i += 1
