#!/usr/bin/python

from ds1054z import DS1054Z
import getopt
import serial
import sys
import os
import time
import numpy as np
import binascii
import matplotlib.pyplot as plt

IP_ADDR = "10.10.10.4"

def usage():
  print " rigol-new.py, part of the fuckshitfuck toolkit"
  print "------------------------------------------------"
  print " -h : prints this message"
  print " -o : offset to fetch from (halfway on 2ch is at 1500000)"
  print " -n : number of samples per trace"
  print " -c : number of traces to fetch"
  print " -f : savefile"
  print " -i : ip address of rigol scope (5555 must be open)"

START_OFFSET = 1450000
END_OFFSET = 1800000
TRACE_COUNT = 5
RAND_LEN = 16
SAVEFILE = "lol.npz"
TEST_MODE = False

if __name__ == "__main__":
  opts,remainder = getopt.getopt(sys.argv[1:],"hi:o:n:c:f:t",["help","ip=","offset=","samples=","count=","file=","test"])
  for (opt,arg) in opts:
    if opt in ("-h","--help"):
      usage()
      sys.exit(0)
    elif opt in ("-o","--offset"):
      START_OFFSET = int(arg)
    elif opt in ("-f","--file"):
      SAVEFILE = arg
    elif opt in ("-n","--samples"):
      NUM_SAMPLES = int(arg)
      END_OFFSET = START_OFFSET + int(arg)
    elif opt in ("-c","--count"):
      TRACE_COUNT = int(arg)
    elif opt in ("-t","--test"):
      TEST_MODE = True
    elif opt in ("-i","--ip"):
      IP_ADDR = arg

NUM_SAMPLES = END_OFFSET - START_OFFSET
print "Sample count is %d" % NUM_SAMPLES

try:
  scope = DS1054Z(IP_ADDR)
except:
  print "Could not connect to %s, can you netcat to 5555?" % IP_ADDR
scope.write(":STOP")
scope.write(":CHAN1:SCAL 0.001")
scope.write(":CHAN1:OFFS -0.055")

print "Scale: {0}V".format(DS1054Z.format_si_prefix(scope.get_channel_scale(1)))

scope.write(":CHAN2:SCAL 5.0")
scope.write(":CHAN2:OFFS 0.0")
scope.write(":TRIG:MODE EDGE")
scope.write(":TRIG:EDGE:SOUR CHAN2")
scope.write(":TRIG:EDGE:LEV 2.0")
scope.write(":TRIG:EDGE:SWE SING")
scope.write(":WAV:SOUR CHAN1")
ser = serial.Serial('/dev/ttyUSB0',9600)

traces = np.zeros((TRACE_COUNT,NUM_SAMPLES),np.float32)
data = np.zeros((TRACE_COUNT,RAND_LEN),np.uint8)
data_out = np.zeros((TRACE_COUNT,RAND_LEN),np.uint8)

for i in range(0,TRACE_COUNT):
  scope.write(":STOP")
  scope.single()
  rand_input = os.urandom(RAND_LEN)
  ser.write("e%s\n" % binascii.hexlify(rand_input))
  ctx_out = ser.readline().rstrip()
  time.sleep(0.5)
  datax = scope.get_waveform_samples("CHAN1",mode="RAW",start=START_OFFSET+1,end=END_OFFSET)
  if TEST_MODE is True:
    print "Test mode, counting useful cycles..."
    data_trigger = scope.get_waveform_samples("CHAN2",mode="RAW",start=START_OFFSET+1,end=END_OFFSET)
    firstTrigger = 0
    lastTrigger = 0
    for i in range(0,len(data_trigger)):
      if data_trigger[i] > 2.0 and firstTrigger == 0:
        # print "SET TRIGGER %d" % i
        firstTrigger = i
      elif data_trigger[i] < 1.0 and firstTrigger != 0:
        # print "END TRIGGER %d" % i
        lastTrigger = i
        break
    if lastTrigger == 0:
      lastTrigger = i
    print "FIRST TRIGGER: %d" % firstTrigger
    print "LAST TRIGGER: %d" % lastTrigger
    print "USEFUL SAMPLES: %d"  % (lastTrigger - firstTrigger)
    # get ready for some mother fucking matplotlib magic
    fig,ax1 = plt.subplots()
    ax1.plot(data_trigger)
    ax2 = ax1.twinx()
    ax2.plot(datax)
    fig.tight_layout()
    plt.show()
    sys.exit(0)
  if len(ctx_out) != (RAND_LEN * 2) + 1:
    os.sleep(3.0)
    print "waiting for device stability..."
    continue
  print "%s:%s" % (binascii.hexlify(rand_input),ctx_out[1:])
  # print "SAVING TRACE"
  traces[i,:] = [np.float32(d) for d in datax]
  data[i,:] = [ord(x) for x in rand_input]
  data_out[i,:] = [ord(x) for x in binascii.unhexlify(ctx_out[1:])]

np.savez(SAVEFILE,traces=traces,data=data,data_out=data_out,freq=[250000000])
scope.run()
scope.close()
ser.close()
