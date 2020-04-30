#!/usr/bin/env python3

from ds1054z import DS1054Z
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException
import random
import getopt
import serial
import sys
import os
import time
import numpy as np
import binascii
import uuid
import support.filemanager

IP_ADDR = "192.168.33.6"

class SIMController:
  def __init__(self):
    self.c = None      # fuck pyscard. seriously.
    pass

  def french_apdu(self,rand=None,autn=None,scope=None,debug=False):
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if debug:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x08, 0x04, 0x02, 0x2f, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    r,sw1,sw2 = self.c.transmit([0x00,0xB2,0x01,0x04] + [r[7]])
    r,sw1,sw2 = self.c.transmit([0x00,0xA4,0x04,0x04] + list(r[3:4 + r[3]]))
    scope.arm()
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    if rand is None and autn is None:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + [0xaa] * 16 + [0x10] + [0xbb] * 16
    else:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + rand + [0x10] + autn
    r,sw1,sw2 = self.c.transmit(authcmd)


def usage():
  print(" rigol-new.py, part of the fuckshitfuck toolkit")
  print("------------------------------------------------")
  print(" -h : prints this message")
  print(" -o : offset to fetch from (halfway on 2ch is at 1500000)")
  print(" -n : number of samples per trace")
  print(" -c : number of traces to fetch")
  print(" -f : savefile")
  print(" -i : ip address of rigol scope (5555 must be open)")

START_OFFSET = 0 # 1400000
END_OFFSET = 1900000
TRACE_COUNT = 5
RAND_LEN = 16
SAVEFILE = "%s.traces" % uuid.uuid4()
NUM_SAMPLES = 10000
TEST_MODE = False

if __name__ == "__main__":
  opts,remainder = getopt.getopt(sys.argv[1:],"hi:o:n:c:w:t",["help","ip=","offset=","samples=","count=","writefile=","test"])
  for (opt,arg) in opts:
    if opt in ("-h","--help"):
      usage()
      sys.exit(0)
    elif opt in ("-o","--offset"):
      START_OFFSET = int(arg)
    elif opt in ("-w","--writefile"):
      SAVEFILE = arg
    elif opt in ("-n","--samples"):
      NUM_SAMPLES = int(arg)
    elif opt in ("-c","--count"):
      TRACE_COUNT = int(arg)
    elif opt in ("-t","--test"):
      TEST_MODE = True
    elif opt in ("-i","--ip"):
      IP_ADDR = arg

if START_OFFSET == 0:
  print("You MUST supply the -o (offset) argument for Rigol scopes")
  sys.exit(0)

END_OFFSET = START_OFFSET + NUM_SAMPLES
# NUM_SAMPLES = END_OFFSET - START_OFFSET
print("Sample count is %d" % NUM_SAMPLES)

sc = SIMController()

try:
  scope = DS1054Z(IP_ADDR)
  print("OK, Scope good")
except:
  print("Could not connect to %s, can you netcat to 5555?" % IP_ADDR)
scope.write(":STOP")

# atmega test
# scope.write(":CHAN1:SCAL 0.010")
# scope.write(":CHAN1:OFFS -0.055")
scope.write(":CHAN1:SCAL 0.050")
scope.write(":CHAN1:OFFS 0.000")

print("Scale: {0}V".format(DS1054Z.format_si_prefix(scope.get_channel_scale(1))))

scope.write(":CHAN2:SCAL 5.0")
scope.write(":CHAN2:OFFS 0.0")
scope.write(":TRIG:MODE EDGE")
scope.write(":TRIG:EDGE:SOUR CHAN2")
scope.write(":TRIG:EDGE:LEV 2.0")
scope.write(":TRIG:EDGE:SWE SING")
scope.write(":WAV:SOUR CHAN1")
# ser = serial.Serial('/dev/ttyUSB0',9600)

traces = np.zeros((TRACE_COUNT,NUM_SAMPLES),np.float32)
data = np.zeros((TRACE_COUNT,RAND_LEN),np.uint8)
data_out = np.zeros((TRACE_COUNT,RAND_LEN),np.uint8)

tm = support.filemanager.TraceManager(SAVEFILE)
BUFFERSIZE = 1000
bufferedTraces = 0

for i in range(0,TRACE_COUNT):
  next_rand = [random.randint(0,255) for _ in range(16)]
  next_autn = [random.randint(0,255) for _ in range(16)]
  scope.write(":STOP")
  scope.single()
  time.sleep(1.0)
  rand_input = os.urandom(RAND_LEN)
  # ser.write("e%s\n" % binascii.hexlify(rand_input))
  # ctx_out = ser.readline().rstrip()
  time.sleep(0.5)
  datax = scope.get_waveform_samples("CHAN1",mode="RAW",start=START_OFFSET+1,end=END_OFFSET)
  if TEST_MODE is True:
    print("Test mode, counting useful cycles...")
    data_trigger = scope.get_waveform_samples("CHAN2",mode="RAW",start=START_OFFSET+1,end=END_OFFSET)
    first_useful = next(x[0] for x in enumerate(data_trigger) if x[1] > 1.0)
    last_useful = next(x[0] for x in enumerate(data_trigger[first_useful:]) if x[1] < 1.0)
    print("Start Capture: (-o) %d" % START_OFFSET)
    print("Num Samples: (-n) %d" % (END_OFFSET - START_OFFSET))
    print("First useful: %d" % first_useful)
    print("Last useful: %d" % last_useful)
    print(data_trigger[0:50])
    sys.exit(0)
  if len(ctx_out) != (RAND_LEN * 2) + 1:
    time.sleep(3.0)
    print("waiting for device stability...")
    continue
  print("%s:%s" % (binascii.hexlify(rand_input),ctx_out[1:]))
  # print "SAVING TRACE"
  traces[i,:] = [np.float32(d) for d in datax]
  data[i,:] = next_rand
  data_out[i,:] = next_autn
  bufferedTraces += 1
  if i != 0 and i % BUFFERSIZE == 0:
    tm.saveBlock(traces,data,data_out)
    traces = np.zeros((TRACE_COUNT,NUM_SAMPLES),np.float32)
    data = np.zeros((TRACE_COUNT,RAND_LEN),np.uint8)
    data_out = np.zeros((TRACE_COUNT,RAND_LEN),np.uint8)
    bufferedTraces = 0

if bufferedTraces != 0:
  tm.saveBlock(traces[0:bufferedTraces],data[0:bufferedTraces],data_out[0:bufferedTraces])
  
tm.cleanup()

# support.filemanager.save(SAVEFILE,traces=traces,data=data,data_out=data_out)
scope.run()
scope.close()
ser.close()
