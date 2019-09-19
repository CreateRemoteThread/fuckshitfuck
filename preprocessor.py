#!/usr/bin/env python3

from scipy.signal import butter,lfilter,freqz
from numpy import *
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

CONFIG_USE_LOWPASS = False

# config of lowpass filter
CONFIG_SAMPLERATE = 124999999
CONFIG_CUTOFF=60000
CONFIG_ORDER=5
CONFIG_REFTRACE = 0

# how big is your window
CONFIG_WINDOW_OFFSET = 10000
CONFIG_WINDOW_LENGTH = 5000
CONFIG_WINDOW_SLIDE = 4000
CONFIG_SAD_CUTOFF = 3.2
CONFIG_MCF_CUTOFF = 0.3

USE_MAXCORR = 1
USE_MINSAD = 2

CONFIG_STRATEGY = USE_MAXCORR

def getSingleSAD(array1,array2):
  totalSAD = 0.0
  return sum(abs(array1 - array2))

def getMaxCorrCoeff(trace1,trace2):
  maxCf = -1.0
  maxCfIndex = 0
  # print(trace1[0:10])
  # print(trace2[0:10])
  for i in range(0,CONFIG_WINDOW_SLIDE):
    r1 = trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i]
    r2 = trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH]
    r = corrcoef(r1,r2)
    if r[0,1] > maxCf:
      maxCf = r[0,1]
      maxCfIndex = i
  for i in range(-CONFIG_WINDOW_SLIDE,0):
    r1 = trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i]
    r2 = trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH]
    r = corrcoef(r1,r2)
    # print(r)
    if r[0,1] > maxCf:
      maxCf = r[0,1]
      maxCfIndex = i
  return (maxCf,maxCfIndex)
 
def getMinimalSAD(trace1,trace2):
  minimalSAD = 500.0
  minimalSADIndex = 0.0
  # print(trace1[0:10])
  # print(trace2[0:10])
  for i in range(0,CONFIG_WINDOW_SLIDE):
    ms = getSingleSAD(trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i],trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH])
    if ms < minimalSAD:
      minimalSAD = ms
      minimalSADIndex = i
  for i in range(-CONFIG_WINDOW_SLIDE,0):
    if CONFIG_WINDOW_OFFSET + i > 0:
      ms = getSingleSAD(trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i],trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH])
      if ms < minimalSAD:
        minimalSAD = ms
        minimalSADIndex = i
  return (minimalSADIndex,minimalSAD)

def printConfig():
  print("Lowpass configuration:")
  print("Cutoff = %d Hz" % CONFIG_CUTOFF)
  print("Samplerate = %d Hz" % CONFIG_SAMPLERATE)
  print("Order = %d" % CONFIG_ORDER)
  print("Sliding Window configuration:")
  print("Window offset: %d samples" % CONFIG_WINDOW_OFFSET)
  print("Max slide = %d samples" % CONFIG_WINDOW_SLIDE)
  print("Window length = %d samples" % CONFIG_WINDOW_LENGTH)

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("Lowpass>MinSAD Pre-processor Utility")
    print("Usage: ./sad-preprocessor.py [in.npz] [out.npz]")
    sys.exit(0)
  printConfig()
  savedDataIndex = 0
  df = load(sys.argv[1],mmap_mode='r')
  if CONFIG_USE_LOWPASS:
    ref = butter_lowpass_filter(df['traces'][CONFIG_REFTRACE],CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
  else:
    ref = df['traces'][CONFIG_REFTRACE]
  numTraces = len(df['traces'])
  sampleCnt = len(df['traces'][0])
  print("Sample count is %d" % sampleCnt)
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  print("----------------------------------------------------")
  if CONFIG_STRATEGY == USE_MINSAD:
    for i in range(0,len(df['traces'])):
      x = df['traces'][i]
      if CONFIG_USE_LOWPASS:
        r2 = butter_lowpass_filter(x,CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
      else:
        r2 = x
      # (msv,msi) = getMaxCorrCoeff(r2,ref)
      (msi,msv) = getMinimalSAD(r2,ref)
      if msv < CONFIG_SAD_CUTOFF:
        if msi == -CONFIG_WINDOW_SLIDE or msi == CONFIG_WINDOW_SLIDE - 1:
          print("Index %d, discarding (edge MSI = not found)" % i)
        else:
          print("Index %d, Minimal SAD Slide %d Samples, Minimal SAD Value %f" % (i,msi,msv))
          traces[savedDataIndex,:] = roll(x,msi)      
          data[savedDataIndex,:] = df['data'][i]
          data_out[savedDataIndex,:] = df['data_out'][i]
          savedDataIndex += 1
      else:
        print("Index %d, discarding (MSV is %f)" % (i,msv))
  elif CONFIG_STRATEGY == USE_MAXCORR:
    for i in range(0,len(df['traces'])):
      x = df['traces'][i]
      if CONFIG_USE_LOWPASS:
        r2 = butter_lowpass_filter(x,CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
      else:
        r2 = x
      (msv,msi) = getMaxCorrCoeff(r2,ref)
      # (msi,msv) = getMinimalSAD(r2,ref)
      if msv > CONFIG_MCF_CUTOFF:
        if msi == -CONFIG_WINDOW_SLIDE or msi == CONFIG_WINDOW_SLIDE - 1:
          print("Index %d, discarding (edge Max Coeff Index = not found, mcf is %f)" % (i,msv))
        else:
          print("Index %d, Max Corr Coeff Slide %d Samples, Max CF Value %f" % (i,msi,msv))
          traces[savedDataIndex,:] = roll(x,msi)
          data[savedDataIndex,:] = df['data'][i]
          data_out[savedDataIndex,:] = df['data_out'][i]
          savedDataIndex += 1
      else:
        print("Index %d, discarding (MSV is %f, index is %d)" % (i,msv,msi))
  print("Saving %d records" % savedDataIndex)
  savez(sys.argv[2],traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex],freq=df['freq'])
