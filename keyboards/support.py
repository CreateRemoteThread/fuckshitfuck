#!/usr/bin/env python3

import numpy as np
import sys
import getopt
import glob
from scipy import signal

CONFIG_THRESHOLD = 0.15
CONFIG_PEAK_IDENTIFY = CONFIG_THRESHOLD
CONFIG_MAX_PULSEWIDTH = 75000

def block_preprocess_function(dslice):
  # fx,Pxx_spec = signal.welch(dslice,124999999,'flattop',1024,scaling='spectrum')
  # return np.sqrt(Pxx_spec)
  return abs(dslice)

def specialk(val):
  if val < 0.02:
    return 0.0
  else:
    return val

# CONFIG_LOWPEAK_IDENTIFY = 0.02
CONFIG_LOWPEAK_BACKOFF = 100

# findFirstPeak is a dirty hack for the a/s problem
# to let us sort by 
def findReallyLocalMaxima(c0,relativePeaks=True,findFirstPeak=False):
  peaks,props = signal.find_peaks(c0,height=np.percentile(c0,99.95),distance=150)
  if len(peaks) == 0:
    print("findReallyLocalMaxima: no peaks detected?")
    sys.exit(0)
  firstPeak = peaks[0]
  if findFirstPeak:
    return firstPeak
  if relativePeaks is False:
    firstPeak = 0
  return [(p-firstPeak,c0[p]) for p in peaks]

# finds the big spikes. use this first.
def findLocalMaxima(data):
  localMaxima = []
  i = 0
  while i < len(data):
    if data[i] >= CONFIG_PEAK_IDENTIFY:
      if i + CONFIG_MAX_PULSEWIDTH > len(data):
        print("findLocalMaxima(): ending peak detection early")
        break
      localMaxima.append(i)
      i += 1000
    i += 1
  return localMaxima

def convertFromHashmap(coeffs):
  c_list = []
  for k in coeffs.keys():
    c_list.append( (k,coeffs[k]) )
  c_list.sort(key=lambda tup:tup[1])
  return c_list[::-1]

def twoOfThree_logWeight(f_in):
  # return f_in
  if f_in > 0.95:
    # print("Extremely strong match")
    return f_in * 2
  elif f_in < 0.5:
    return f_in * 0.5
  else:
    return f_in

def twoOfThree_twinlinked(unknown,alignment):
  lm = findLocalMaxima(unknown[0])
  maxCorr = {}
  for local_max in lm:
    dataA = block_preprocess_function(unknown[0][local_max:local_max + CONFIG_MAX_PULSEWIDTH])
    dataB = block_preprocess_function(unknown[1][local_max:local_max + CONFIG_MAX_PULSEWIDTH])
    for k in alignment.keys():
      (alignData,alignMax) = alignment[k]
      for align_max in alignMax:
        alignA = block_preprocess_function(alignData[0][align_max:align_max + CONFIG_MAX_PULSEWIDTH])
        alignB = block_preprocess_function(alignData[1][align_max:align_max + CONFIG_MAX_PULSEWIDTH])
        lcorrA = np.corrcoef(dataA,alignA)[0,1]
        lcorrB = np.corrcoef(dataB,alignB)[0,1]
        if k in maxCorr.keys():
          maxCorr[k] += twoOfThree_logWeight(lcorrA) + twoOfThree_logWeight(lcorrB)
        else:
          maxCorr[k] = twoOfThree_logWeight(lcorrA) + twoOfThree_logWeight(lcorrB)
  maxCorrCoef = 0
  maxKey = ""
  for k in maxCorr.keys():
    if maxCorr[k] > maxCorrCoef:
      maxCorrCoef = maxCorr[k]
      maxKey = k
  return (maxKey,maxCorr)

CONFIG_FILENAME = None
CONFIG_TRAIN = None

def extract_2channel_spectrum(data):
  out = []
  for lmA in findLocalMaxima(data[0]):
    dataASlice = data[0][lmA:lmA+CONFIG_MAX_PULSEWIDTH]
    dataBSlice = data[1][lmA:lmA+CONFIG_MAX_PULSEWIDTH]
    out.append(  (block_preprocess_function(dataASlice),block_preprocess_function(dataBSlice)) )
  return out

def pool_agreement(tr):
  for (i,d_spectra) in training:
    print("Calculating spectral alignment for %s" % i)
    for d_spec in d_spectra:
      print("+")


def getSAD(t1,t2):
  return sum(abs(t1-t2))

def correlate_spectra_minsad(data_in,training):
  data_specA = block_preprocess_function(data_in[0])
  data_specB = block_preprocess_function(data_in[1])
  focuses = {}
  print(len(training))
  for (i,d_spectra) in training:
    for d_spec in d_spectra:
      xc = getSAD(data_specA,d_spec[0]) + getSAD(data_specB,d_spec[1])
      if i in focuses.keys():
        focuses[i] += [xc]
      else:
        focuses[i] = [xc]
  print(focuses)
  for i in focuses.keys():
    focuses[i] = min(focuses[i])
  print(min(focuses.items(), key=lambda item: item[1]))
  return

def correlate_spectra(data_in,training):
  data_specA = block_preprocess_function(data_in[0])
  data_specB = block_preprocess_function(data_in[1])
  focuses = {}
  print(len(training))
  for (i,d_spectra) in training:
    for d_spec in d_spectra:
      xc = np.corrcoef(data_specA,d_spec[0])[0,1] + np.corrcoef(data_specB,d_spec[1])[0,1]
      if xc < (0.98*2):
        # print("Discarding: nonmatch %f " % xc)
        continue
      # print("2-channel correlation : %f" % xc)
      if i in focuses.keys():
        focuses[i] += [xc]
      else:
        focuses[i] = [xc]
  for i in focuses.keys():
    focuses[i] = np.average(focuses[i])
  print(max(focuses.items(), key=lambda item: item[1]))
  return

if __name__ == "__main__":
  print("support.py - don't call this directly")
