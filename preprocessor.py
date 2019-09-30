#!/usr/bin/env python3

import scipy.io
from scipy.signal import butter,lfilter,freqz
from numpy import *
import getopt
import sys
import support.filemanager

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
CONFIG_ORDER=1
CONFIG_REFTRACE = 0

# how big is your window
CONFIG_WINDOW_OFFSET = 103628
CONFIG_WINDOW_LENGTH = 44355
CONFIG_WINDOW_SLIDE = 5000
CONFIG_SAD_CUTOFF = 3.2
CONFIG_MCF_CUTOFF = 0.9

CONFIG_BUCKETSIZE = None

USE_MAXCORR = 1
USE_MINSAD = 2
DO_LOWPASS = 3
DO_SAVECW = 4
DO_SAVEMAT = 5

CONFIG_STRATEGY = USE_MAXCORR

CONFIG_INFILE = None
CONFIG_OUTFILE = None

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

def printHelp():
  print("Preprocessor utility.")
  print(" -h : print this message")
  print(" -f <file> : specify input file")
  print(" -w <file> : specify output file")
  print(" -strategy [CORRCOEFF,SAD,LOWPASS] : specify preprocess strategy")
  print("           [SAVEMAT,SAVECW] : convert trace file format")
  print(" -c <cutoff> : specify max SAD cutoff OR min correlation coeff cutoff")
  print("             : everything not matching this is discarded!!!!")
  print(" -l <cutoff,samplerate,order> : lowpass before preprocessing")
  print(" --window-offset <offset> : offset of window to match in samples")
  print(" --window-length <length> : length of window to match in samples")
  print(" --window-slide <maxslide> : max num of samples to slide the window to search for a match")
  print("                           : this is effectively doubled for sliding backwards")
  print(" -r <reftrace> : specify index of reference trace")

def printConfig():
  print("-----------------------------------------------------")
  print(" Preprocessor Configuration:")
  print(" Input file = %s" % CONFIG_INFILE)
  print(" Output file = %s" % CONFIG_OUTFILE)
  if CONFIG_STRATEGY == USE_MAXCORR:
    print(" Strategy: Maximize correlation coefficient")
  elif CONFIG_STRATEGY == USE_MINSAD:
    print(" Strategy: Minimize Sum of Absolute Difference")
  elif CONFIG_STRATEGY == DO_LOWPASS:
    print(" Action: Apply Lowpass and Save")
  if CONFIG_USE_LOWPASS:
    print(" Use Lowpass: yes")
    print("   Lowpass Sample Rate: %d Hz" % CONFIG_SAMPLERATE)
    print("   Lowpass Cutoff: %d Hz" % CONFIG_CUTOFF)
    print("   Lowpass Order: %d" % CONFIG_ORDER)
  else:
    print(" Use Lowpass: no")
  if CONFIG_STRATEGY in (USE_MAXCORR,USE_MINSAD):
    print(" Window configuration:")
    print("   Window offset: %d samples" % CONFIG_WINDOW_OFFSET)
    print("   Max slide = %d samples" % CONFIG_WINDOW_SLIDE)
    print("   Window length = %d samples" % CONFIG_WINDOW_LENGTH)
  if CONFIG_BUCKETSIZE is None:
    print(" No bucket configured")
  else:
    print(" Bucket size set at %d" % CONFIG_BUCKETSIZE)
  print("-----------------------------------------------------")

if __name__ == "__main__":
  optlist,args = getopt.getopt(sys.argv[1:],"hf:w:l:r:c:b:",["help","strategy=","lowpass=","reftrace=","window-offset=","window-length=","window-slide=","cutoff=","bucketsize="])
  for arg, value in optlist:
    if arg == "-f":
      CONFIG_INFILE = value
    elif arg == "-w":
      CONFIG_OUTFILE = value
    elif arg in ("-h","--help"):
      printHelp()
    elif arg == "--strategy":
      if value.upper() in ("CORRCOEF","CORRCOEFF"):
        CONFIG_STRATEGY = USE_MAXCORR
      elif value.upper() in ("SAD","SADNESS"):
        CONFIG_STRATEGY = USE_MINSAD
      elif value.upper() == "LOWPASS":
        CONFIG_STRATEGY = DO_LOWPASS
      elif value.upper() == "SAVEMAT":
        CONFIG_STRATEGY = DO_SAVEMAT
      elif value.upper() == "SAVECW":
        CONFIG_STRATEGY = DO_SAVECW
      else:
        print("Invalid preprocessing strategy. Valid options are CORRCOEF,SAD,LOWPASS,SAVEMAT,SAVECW (SAVECW does not need filename)")
        sys.exit(0)
    elif arg in ("-l","--lowpass"):
      try:
        (str_cutoff,str_samplerate,str_order) = value.split(",")
        CONFIG_USE_LOWPASS = True
        CONFIG_CUTOFF = int(str_cutoff)
        CONFIG_SAMPLERATE = int(str_samplerate)
        CONFIG_ORDER = int(str_order)
      except:
        print("Invalid lowpass filter. Specify as CUTOFF,SAMPLERATE,ORDER")
        sys.exit(0)
    elif arg in ("-r","--reftrace"):
      CONFIG_REFTRACE = int(value)
    elif arg == "--window-length":
      print("Configuring window length...")
      CONFIG_WINDOW_LENGTH = int(value)
    elif arg == "--window-offset":
      CONFIG_WINDOW_OFFSET = int(value)
    elif arg == "--window-slide":
      CONFIG_WINDOW_SLIDE = int(value)
    elif arg in ("-b","--bucketsize"):
      CONFIG_BUCKETSIZE = int(value)
    elif arg in ("-c","--cutoff"):
      CONFIG_SAD_CUTOFF = float(value)
      CONFIG_MCF_CUTOFF = float(value)
  if CONFIG_INFILE is None or CONFIG_OUTFILE is None and CONFIG_STRATEGY != DO_SAVECW:
    print("You must specify input (-f) and output files (-w)")
    sys.exit(0)
  printConfig()
  savedDataIndex = 0
  df = support.filemanager.load(CONFIG_INFILE)
  if CONFIG_USE_LOWPASS:
    ref = butter_lowpass_filter(df['traces'][CONFIG_REFTRACE],CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
  else:
    ref = df['traces'][CONFIG_REFTRACE]
  numTraces = len(df['traces'])
  sampleCnt = len(df['traces'][0])
  print(" + Sample count is %d" % sampleCnt)
  print(" + Trace count is %d" % numTraces)
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  print("----------------------------------------------------")
  if CONFIG_STRATEGY == USE_MINSAD:
    for i in range(0,len(df['traces'])):
      x = df['traces'][i]
      if CONFIG_BUCKETSIZE is not None:
        if savedDataIndex == CONFIG_BUCKETSIZE:
          print("The bucket is full, not processing any more...!")
          break
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
          traces[savedDataIndex,:] = roll(x,-msi)      
          data[savedDataIndex,:] = df['data'][i]
          data_out[savedDataIndex,:] = df['data_out'][i]
          savedDataIndex += 1
      else:
        print("Index %d, discarding (MSV is %f)" % (i,msv))
  elif CONFIG_STRATEGY == USE_MAXCORR:
    for i in range(0,len(df['traces'])):
      x = df['traces'][i]
      if CONFIG_BUCKETSIZE is not None:
        if savedDataIndex == CONFIG_BUCKETSIZE:
          print("The bucket is full, not processing any more...!")
          break
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
          traces[savedDataIndex,:] = roll(x,-msi)
          data[savedDataIndex,:] = df['data'][i]
          data_out[savedDataIndex,:] = df['data_out'][i]
          savedDataIndex += 1
      else:
        print("Index %d, discarding (correlation is %f, index is %d)" % (i,msv,msi))
  elif CONFIG_STRATEGY == DO_LOWPASS:
    for i in range(0,len(df['traces'])):
      x = df['traces'][i]
      if CONFIG_BUCKETSIZE is not None:
        if savedDataIndex == CONFIG_BUCKETSIZE:
          print("The bucket is full, not processing any more...!")
          break
      traces[i] = butter_lowpass_filter(x,CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
      data[i] = df['data'][i]
      data_out[i] = df['data_out'][i]
      savedDataIndex += 1
      print("Lowpassed %d" % i)
  elif CONFIG_STRATEGY == DO_SAVEMAT:
    support.filemanager.save_mat(CONFIG_OUTFILE,traces=df["traces"],data=df["data"],data_out=df["data_out"])
    sys.exit(0)
  elif CONFIG_STRATEGY == DO_SAVECW:
    support.filemanager.save_cw(df)
    sys.exit(0)
  print("Saving %d records" % savedDataIndex)
  support.filemanager.save(CONFIG_OUTFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])
