#!/usr/bin/python

import scipy.io
import numpy
import os
import sys

class TraceSet:
  def __init__(self,key):
    print("TraceSet: Initialized blank TraceSet with key %s" % key)
    self.key = key
    self.traces_fn = None
    self.traces = None
    self.data_fn = None
    self.data = None
    self.data_out_fn = None
    self.data_out = None

class TraceManager:
  def cleanup(self):
    print("TraceManager: saveBlock wrapping up")
    if self.f is not None:
      self.f.close()

  def saveBlock(self,traces,data_in,data_out):
    if self.numPoints is not None:
      if len(traces[0]) != self.numPoints:
        print("TraceManager: saveBlock trying to write a trace with incorrect length. Expected %d, trying to write %d" % (self.numPoints, len(traces[0])))
        sys.exit(0)
    if self.f is None:
      print("TraceManager: saveBlock creating new file and data directory")
      self.f = open(self.fn,"w+")
      with cd(self.WR):
        os.mkdir(self.DR)
    else:
      print("TraceManager: saveBlock seeking to file's end")
      self.f.seek(0,2)
    i = self.getNextKey()
    with cd(self.WR):
      print("TraceManager: saveBlock writing to storage...")
      self.dataObj[i] = TraceSet(i)
      self.dataObj[i].traces_fn = "%s/traces-%s.npy" % (self.DR,i) 
      self.dataObj[i].data_fn = "%s/plaintext-%s.npy" % (self.DR,i) 
      self.dataObj[i].data_out_fn = "%s/ciphertext-%s.npy" % (self.DR,i)
      numpy.save(self.dataObj[i].traces_fn,traces)
      numpy.save(self.dataObj[i].data_fn,data_in)
      numpy.save(self.dataObj[i].data_out_fn,data_out)
      self.f.write("traces,%d=%s\n" % (i,self.dataObj[i].traces_fn))
      self.f.write("data_in,%d=%s\n" % (i,self.dataObj[i].data_fn))
      self.f.write("data_out,%d=%s\n" % (i,self.dataObj[i].data_out_fn))
      print("TraceManager: saveBlock refilling dataObj")
      self.dataObj[i].data = numpy.load(self.dataObj[i].data_fn,mmap_mode="r") 
      self.dataObj[i].traces = numpy.load(self.dataObj[i].traces_fn,mmap_mode="r") 
      self.dataObj[i].data_out = numpy.load(self.dataObj[i].data_out_fn,mmap_mode="r")

  def getNextKey(self):
    for i in range(0,65535):
      if i in self.dataObj.keys():
        pass
      else:
        return i

  def __init__(self,filename):
    print("TraceManager: Initializing with filename %s" % filename)
    self.dataObj = {}
    self.fn = filename
    try:
      WORKING_ROOT = "/".join(filename.split("/")[:-1])
    except:
      WORKING_ROOT = "."
    self.WR = WORKING_ROOT
    self.numPoints = None
    print("TraceManager: Setting session WORKING_ROOT to %s" % self.WR)
    baseName = "".join(self.fn.split(".")[:-1])
    self.DR = "%s.data" % baseName
    if os.path.isfile(filename) is False:
      print("TraceManager: %s is not a file, creating a new one" % filename)
      self.f = None # lazy save
      return
    self.f = open(filename,"r+")
    with cd(WORKING_ROOT):
      traceCount = 0
      numPoints = None
      for fl in self.f.readlines():
        if "=" not in fl:
          continue
        (opt,val) = fl.rstrip().split("=")
        (real_opt,opt_num) = opt.split(",")
        if opt_num not in self.dataObj.keys():
          self.dataObj[opt_num] = TraceSet(opt_num)
        if real_opt == "data_in":
          print("TraceManager: Loading file %s as data_in array" % val)
          self.dataObj[opt_num].data_fn = val
          self.dataObj[opt_num].data =numpy.load(val,mmap_mode="r") 
        elif real_opt == "data_out":
          print("TraceManager: Loading file %s as data_out array" % val)
          self.dataObj[opt_num].data_out_fn = val
          self.dataObj[opt_num].data_out =numpy.load(val,mmap_mode="r") 
        elif real_opt == "traces":
          print("TraceManager: Loading file %s as trace array" % val)
          self.dataObj[opt_num].traces_fn = val
          self.dataObj[opt_num].traces = numpy.load(val,mmap_mode="r")
          traceCount += len(self.dataObj[opt_num].traces)
          if numPoints is None:
            numPoints = len(self.dataObj[opt_num].traces[0])
          else:
            newNumPoints = len(self.dataObj[opt_num].traces[0])
            if numPoints != newNumPoints:
              print("TraceManager: Mismatched point count in trace %s - expected %d, got %d" % (val,numPoints,newNumPoints))
              sys.exit(0)
    print("TraceManager: %d traces with %d points each loaded." % (traceCount,numPoints))
    self.traceCount = traceCount
    self.numPoints = numPoints

###########################################################
#################### LEGACY SHIT BELOW ####################
###########################################################

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

def fetch_trace(dataObj=None):
  if dataObj is None:
    print("Nope: you must call this with the original data object")
    sys.exit(0)

def save_mat(fn_,traces=None,data=None,data_out=None,freq=None):
  scipy.io.savemat(fn_,{"traces":traces,"textin":data,"textout":data,"key":[]})

# reference: https://wiki.newae.com/File_Formats
def save_cw(dataObj=None):
  if dataObj is None:
    print("Nope: you must call this with the original data object")
    sys.exit(0)
  else:
    fn = dataObj["orig_fn"]
    SYMLINK_ROOT = "/".join(fn.split("/")[:-1])
    traces = dataObj["traces"]
    baseName = "".join(fn.split(".")[:-1])
    WORKING_ROOT = "%s.data/" % baseName
    with cd(SYMLINK_ROOT):
      os.system("ln -s %s %s/save_cw_traces.npy" % (dataObj["traces_fn"].split("/")[1],WORKING_ROOT))
      os.system("ln -s %s %s/save_cw_textin.npy" % (dataObj["data_fn"].split("/")[1],WORKING_ROOT))
      os.system("ln -s %s %s/save_cw_textout.npy" % (dataObj["data_out_fn"].split("/")[1],WORKING_ROOT))
      os.system("ln -s %s %s/save_cw_keylist.npy" % (dataObj["data_out_fn"].split("/")[1],WORKING_ROOT))
    with cd(WORKING_ROOT):
      f = open("project.cwp","w")
      f.write("[Trace Management]\n")
      f.write("tracefile0 = test.cfg\n")
      f.write("enabled0 = True\n")
      f.write("[ChipWhisperer]\n")
      f.write("[[General Settings]]\n")
      f.write("Project Name = Untitled\n")
      f.write("Program Name = ChipWhisperer\n")
      f.close()
      f = open("test.cfg","w")
      f.write("[Trace Config]\n") 
      f.write("numTraces = %d\n" %len(traces)) 
      f.write("format = native\n") 
      f.write("numPoints = %d\n" % len(traces[0])) 
      f.write("prefix = save_cw_\n") 
      f.write("scopeSampleRate = 0\n") 
      f.close()
      # df["traces_fn"].split("/")[1]
      # sys.exit(0)
      print("Done. You can load %s/project.cwp" % WORKING_ROOT)

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
  dataObj["orig_fn"] = fn
  try:
    WORKING_ROOT = "/".join(fn.split("/")[:-1])
  except:
    WORKING_ROOT = "."
  with cd(WORKING_ROOT):
    f = open(fn,"r")
    for f_ in f.readlines():
      l = f_.rstrip()
      (arg,val) = l.split("=")
      # backward compatibility fix
      if arg == "traces,0" or arg == "traces":
        print("* Loading %s as trace array" % val)
        dataObj["traces_fn"] = val
        dataObj["traces"] = numpy.load(val,mmap_mode="r")
      elif arg == "data_in,0" or arg == "data_in":
        print("* Loading %s as data_in" % val)
        dataObj["data_fn"] = val
        dataObj["data"] = numpy.load(val,mmap_mode="r")
      elif arg == "data_out,0" or arg == "data_out":
        print("* Loading %s as data_out" % val)
        dataObj["data_out_fn"] = val
        dataObj["data_out"] = numpy.load(val,mmap_mode="r")
      elif arg == "sr":
        dataObj["sr"] = int(val) 
      else:
        dataObj[arg] = val
    f.close()
    traceCount = len(dataObj["traces"])
    numPoints = len(dataObj["traces"][0])
    print("%d traces with %d points each loaded." % (traceCount,numPoints))
    return dataObj

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("This is not meant to be called directly :)")
  else:
    tm = TraceManager(sys.argv[1])
