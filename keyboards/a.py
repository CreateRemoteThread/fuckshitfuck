#!/usr/bin/env python3

from picoscope import ps2000a
import matplotlib as mpl
import numpy as np
import sys
import support
import getopt
import time

mpl.use("Agg")
import matplotlib.pyplot as plt
CONFIG_SAMPLECOUNT = 400000
CONFIG_SAMPLERATE = 124999999
CONFIG_CAPTURES = 5

CONFIG_THRESHOLD = support.CONFIG_THRESHOLD
CONFIG_BACKOFF = 0.2
CONFIG_VRANGE = 0.5

CONFIG_FPREFIX = None

def confirmSettings():
  print("Number of captures: %d" % CONFIG_CAPTURES)
  print("Sample rate: %d" % CONFIG_SAMPLERATE)
  print("Sample count: %d" % CONFIG_SAMPLECOUNT)
  print("Trigger level: %f" % CONFIG_THRESHOLD)
  print("Analog range: %f" % CONFIG_VRANGE)
  if CONFIG_THRESHOLD > CONFIG_VRANGE:
    print("Trigger cannot exceed analog range. Bye!")
    sys.exit(0)
  if CONFIG_FPREFIX:
    print("Capturing data for: %s" % CONFIG_FPREFIX)
  x = input("Are these settings correct? [y/n] ")
  if x.rstrip() not in ("y","Y"):
    print("Capture action cancelled. Bye!")
    sys.exit(0)

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"c:t:T:v:r:n:",["count=","train=","trigger=","vrange=","samplerate=","samplecount="])
  for opt, arg in opts:
    if opt in ("-c","--count"):
      if arg in ("inf","infinite"):
        CONFIG_CAPTURES = None
      else:
        CONFIG_CAPTURES = int(arg)
    elif opt in ("-T","--trigger"):
      CONFIG_THRESHOLD = float(arg)
    elif opt in ("-v","--vrange"):
      CONFIG_VRANGE = float(arg)
    elif opt in ("-r","--samplerate"):
      CONFIG_SAMPLERATE = int(arg)
    elif opt in ("-n","--samplecount"):
      CONFIG_SAMPLECOUNT = int(arg)
    elif opt in ("-t","--train"):
      CONFIG_FPREFIX = arg
  confirmSettings()
  ps = ps2000a.PS2000a()
  ps.setChannel('A','DC',VRange=CONFIG_VRANGE,VOffset=0.0,enabled=True,BWLimited=False,probeAttenuation=10.0)
  ps.setChannel('B','DC',VRange=CONFIG_VRANGE,VOffset=0.0,enabled=True,BWLimited=False,probeAttenuation=10.0)
  (freq,maxSamples) = ps.setSamplingFrequency(CONFIG_SAMPLERATE,CONFIG_SAMPLECOUNT)
  print(" > Asked for %d Hz, got %d Hz" % (CONFIG_SAMPLERATE, freq))
  if CONFIG_FPREFIX != None:
    print(" > Configured in training mode with prefix %s" % CONFIG_FPREFIX)
  ps.setSimpleTrigger('A',CONFIG_THRESHOLD,'Rising',enabled=True)
  i = 0
  nCount = 0
  nMax = CONFIG_CAPTURES
  while (nMax is None) or (nCount < nMax):
    ps.runBlock()
    ps.waitReady()
    dataA = ps.getDataV('A',CONFIG_SAMPLECOUNT,returnOverflow=False)
    dataB = ps.getDataV('B',CONFIG_SAMPLECOUNT,returnOverflow=False)
    if float(max(dataA[0:100]) < float(CONFIG_THRESHOLD)):
      print("Automatic trigger, keep waiting... (%f < %f)" % (max(dataA[0:100]),CONFIG_THRESHOLD))
      continue
    print("Threshold reached, saving...")
    if CONFIG_FPREFIX is None:
      np.save("floss/%d.npy" % nCount,[dataA,dataB])
      time.sleep(CONFIG_BACKOFF)
      print("Resuming capture...")
    else:
      np.save("toothpicks/%s-%d.npy" % (CONFIG_FPREFIX,nCount),[dataA,dataB])
    nCount += 1
  print("Captured %d samples, task complete." % nCount)
  sys.exit(0)
