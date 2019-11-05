#!/usr/bin/env python3

import numpy as np
import sys
import getopt
import glob
from scipy import signal

CONFIG_PEAK_IDENTIFY = 0.2
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

def findLocalMaxima(data):
  localMaxima = []
  i = 0
  while i < len(data):
    if data[i] >= CONFIG_PEAK_IDENTIFY:
      if i + CONFIG_MAX_PULSEWIDTH > len(data):
        print("findLocalMaxima(): ending peak detection")
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

def usage():
  print("to TRAIN: put training samples in toothpicks/, and use -t <npy> to create a training db")
  print("to MATCH: specify real sample location with -f floss-papaya, and use -t <npy> to specify a training db")
  sys.exit(0)

if __name__ == "__main__":
  print("support.py post-processing tool")
  optlist,args = getopt.getopt(sys.argv[1:],"hf:t:",["help","file=","train="])
  for opt, arg in optlist:
    if opt in ("-h","--help"):
      usage()
    elif opt in ("-f","--file"):
      CONFIG_FILENAME = arg
    elif opt in ("-t","--train"):
      CONFIG_TRAIN = arg
  if CONFIG_TRAIN is None:
    print("You must specify a dataset npz. Exiting...")
    sys.exit(0)
  if CONFIG_FILENAME is None:
    prefixes = []
    df = glob.glob("toothpicks/*-0.npy")
    for fn in df:
      fn_raw = fn.replace("toothpicks/","")
      fn_prefix = fn_raw.split("-")[0]
      prefixes.append(fn_prefix)
    out_spectra = []
    for pf in prefixes:
      df = glob.glob("toothpicks/%s-*.npy" % pf)
      for fn in df:
        data = np.load(fn)
        out_spectra += [(pf,extract_2channel_spectrum(data))]
    print("Saving spectral mask %s" % CONFIG_TRAIN)
    print(len(out_spectra))
    np.save(CONFIG_TRAIN,out_spectra)
  else:
    in_spectra = np.load(CONFIG_TRAIN)
    print("Spectral mask %s loaded" % CONFIG_TRAIN)
    # this expects files in the format %d %d %d
    bCont = True
    i = 0
    while bCont is True:
      try:
        fn = "%s/%d.npy" % (CONFIG_FILENAME,i)
        d = np.load(fn)
      except:
        print("Could not open %s" % fn)
        bCont = False
        continue
      print("Loaded %s" % fn)
      # correlate_spectra(d,in_spectra)
      correlate_spectra_minsad(d,in_spectra)
      i += 1
