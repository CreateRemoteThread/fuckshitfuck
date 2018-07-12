#!/usr/bin/python

import numpy as np
from scipy.signal import butter, lfilter, freqz
from numpy import *
import sys
import glob
import binascii

sbox = [99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22]

def butter_lowpass(cutoff, fs, order=5):
  nyq = 0.5 * fs
  normal_cutoff = cutoff / nyq
  b, a = butter(order, normal_cutoff, btype='low', analog=False)
  return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
  b, a = butter_lowpass(cutoff, fs, order=order)
  y = lfilter(b, a, data)
  return y

def getUsefulTraceLength(fn):
  f = open(fn)
  c = 0
  for l_ in f.readlines():
    (data,size) = l_.rstrip().split(",")
    if np.float32(size) > 0.5:
      c += 1
    else:
      break
  f.close()
  return c

def loadTraces(length,fns):
  data = zeros((length,len(fns)),float32)
  plaintexts = zeros((16,len(fns)),uint8)
  for fn_c in range(0,len(fns)):
    fn = fns[fn_c]
    plaintext = binascii.unhexlify(fn[-36:-4])
    f = open(fn,"r")
    dx = f.readlines()[0:length]
    d = [np.float32(x.rstrip().split(",")[0]) for x in dx]
    f.close()
    # data[:,fn_c] = d
    data[:,fn_c] = butter_lowpass_filter(d,10000,40e6,3)
    plaintexts[:,fn_c] = [uint8(ord(i)) for i in plaintext]
  print "Loaded %d data, %d plaintexts" % (len(data),len(plaintexts))
  return (data,plaintexts)

def deriveKey(data,plaintexts,usefulTraceLength):
  keys = arange(0,16)
  recovKey = ""
  # if len(data) != len(plaintexts):
  # print "Critical: data length %d != plaintexts length %d. Fix your data" % (len(data), len(plaintexts))
  # sys.exit(0)
  varray = zeros((plaintexts[:,1].size,256,16),uint8)
  print data[1,:].size
  # print len(data)
  for i in range(0,16):
    for n in range(0,256):  
      for t in range(0,plaintexts[:,i].size):
        varray[t,n,i] = plaintexts[t,i] ^ n
        varray[t,n,i] = sbox[varray[t,n,i]]
        varray[t,n,i] = bin(varray[t,n,i]).count("1")
  print varray.shape
  print "Calculating mean Hamming weight..."  
  hweight_mean = zeros((varray[1,:,1].size,16),float32)
  for i in range(0,varray[1,:,1].size):
    for n in range(0,16):
      hweight_mean[i,n] = average(varray[:,i,n])
  print "Finding difference from actual H-weight..."
  for i in range(0,16):
    for n in range(0,256):
      varray = varray.astype(float32)
      varray[:n,i] = varray[:n,i] - hweight_mean[n,i]
  print "Calculating mean power traces..."
  powermean = zeros((data[1,:].size),float32)
  for i in range(0,data[1,:].size):
    powermean[i] = average(data[:,i])
  meantraces = data - powermean
  print "Creating correlation matrices..."
  rarray = zeros((256,data[1,:].size,16),float32)
  for i in range(0,16): # BYTE POSN
    for j in range(0,256): # KEY CAND
      rarray[j,:,i] = sum(varray[:,j,i],axis=0) * sum(meantraces,axis=0) / sqrt(sum(varray[:,j,i]**2, axis=0) * sum(meantraces**2, axis=0))
    s = rarray[:,:,i] ** 2
    keys[i] = nonzero(amax(s) == s)[0]
  return keys

if __name__ == "__main__":
  fns = glob.glob("%s/*.csv" % sys.argv[1])
  print "Stage 1: Estimating useful trace size"
  fl = 0.0
  for fn in fns[0:10]:
    fl += getUsefulTraceLength(fn)
  usefulTraceLength = int(fl/10.0) / 10
  print "Stage 1: Estimating round 1 to be %d samples" % (usefulTraceLength)
  print "Stage 2: Loading %d samples from %d traces" % (usefulTraceLength,len(fns))
  data,plaintexts = loadTraces(usefulTraceLength,fns)
  print "Stage 3: Deriving key... wish me luck!"
  r = deriveKey(data,plaintexts,usefulTraceLength)
  print "Done: Recovered key %s" % r
