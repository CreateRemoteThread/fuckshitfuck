#!/usr/bin/python

import numpy
import os
import sys

class cd:
  def __init__(self,newPath):
    self.newPath = os.path.expanduser(newPath)

  def __enter__(self):
    self.savedPath = os.getcwd()
    if self.newPath != '':
      os.chdir(self.newPath)

  def __exit__(self,etype,value,traceback):
    os.chdir(self.savedPath)

def convert(fn):
  BASENAME = fn.replace(".npz","")
  print("Converting basename %s" % BASENAME)
  df = numpy.load(fn)
  save(BASENAME,df["traces"],df["data"],df["data_out"])
  os.remove(fn)

def save(fn_,traces=None,data=None,data_out=None,freq=None):
  if ".npz" in fn_ or ".traces" in fn_:
    print("Do not save as .npz or .traces. Removing suffix")
    fn = fn_.replace(".npz","").replace(".traces","")
  else:
    fn = fn_
  try:
    WORKING_ROOT = "/".join(fn.split("/")[:-1])
  except:
    WORKING_ROOT = "."
  with cd(WORKING_ROOT):
    try:
      DIRBASE = "%s.data" % fn.split("/")[-1]
    except:
      DIRBASE = "%s.data" % fn
    FN_TRACES = "%s/traces.npy" % DIRBASE
    FN_DATA_IN = "%s/plaintext.npy" % DIRBASE
    FN_DATA_OUT = "%s/ciphertext.npy" % DIRBASE
    f = open("%s.traces" % fn,"w")
    f.write("traces=%s\n" % FN_TRACES)
    f.write("data_in=%s\n" % FN_DATA_IN)
    f.write("data_out=%s\n" % FN_DATA_OUT)
    if freq != None:
      f.write("sr=%d\n" % freq)
    f.close() 
    os.mkdir("%s" % DIRBASE)
    numpy.save(FN_TRACES,traces)
    numpy.save(FN_DATA_IN,data)
    numpy.save(FN_DATA_OUT,data_out)

def load(fn):
  dataObj = {}
  try:
    WORKING_ROOT = "/".join(fn.split("/")[:-1])
  except:
    WORKING_ROOT = "."
  with cd(WORKING_ROOT):
    f = open(fn,"r")
    for f_ in f.readlines():
      l = f_.rstrip()
      (arg,val) = l.split("=")
      if arg == "traces":
        print("* Loading %s as trace array" % val)
        dataObj["traces"] = numpy.load(val,mmap_mode="r")
      elif arg == "data_in":
        print("* Loading %s as data_in" % val)
        dataObj["data"] = numpy.load(val,mmap_mode="r")
      elif arg == "data_out":
        print("* Loading %s as data_out" % val)
        dataObj["data_out"] = numpy.load(val,mmap_mode="r")
      elif arg == "sr":
        dataObj["sr"] = int(val) 
    f.close()
    return dataObj

if __name__ == "__main__":
  # save("/media/talos/CORROSION/test-save",[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5])
  # df = load("/media/talos/CORROSION/test-save.traces")
  # print(df["data"])
  if len(sys.argv) != 2:
    print("This is not meant to be called directly :)")
  else:
    convert(sys.argv[1])
