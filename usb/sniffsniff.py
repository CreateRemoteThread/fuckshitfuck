#!/usr/bin/env python3

import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc
import time

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open PicoScope 2000 Series device
# Returns handle to chandle for use in future API functions
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])

enabled = 1
disabled = 0
analogue_offset = 0.0

# Set up channel A
# handle = chandle
# channel = PS2000A_CHANNEL_A = 0
# enabled = 1
# coupling type = PS2000A_DC = 1
# range = PS2000A_2V = 7
# analogue offset = 0 V
channel_range = ps.PS2000A_RANGE['PS2000A_50MV']
status["setChA"] = ps.ps2000aSetChannel(chandle,
                    ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'],
                    enabled,
                    ps.PS2000A_COUPLING['PS2000A_DC'],
                    channel_range,
                    analogue_offset)
assert_pico_ok(status["setChA"])

sizeOfOneBuffer = 5000
numBuffersToCapture = 40

totalSamples = sizeOfOneBuffer * numBuffersToCapture
bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)

memory_segment = 0

status["setDataBuffersA"] = ps.ps2000aSetDataBuffers(chandle,
                           ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'],
                           bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                           None,
                           sizeOfOneBuffer,
                           memory_segment,
                           ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])
assert_pico_ok(status["setDataBuffersA"])

maxADC = ctypes.c_int16()
status["maximumValue"] = ps.ps2000aMaximumValue(chandle, ctypes.byref(maxADC))
assert_pico_ok(status["maximumValue"])
print("Max ADC Value: %d" % maxADC.value)

# 6500 = (max adc value / 50mV) * 15

status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 0, int(mV2adc(10,channel_range,maxADC)), 2, 0, 0)
assert_pico_ok(status["trigger"])

# Begin streaming mode:
sampleInterval = ctypes.c_int32(64)
sampleUnits = ps.PS2000A_TIME_UNITS['PS2000A_NS']
maxPreTriggerSamples = 0
autoStopOn = 1
downsampleRatio = 1
def runStreaming():
  status["runStreaming"] = ps.ps2000aRunStreaming(chandle,
                          ctypes.byref(sampleInterval),
                          sampleUnits,
                          maxPreTriggerSamples,
                          totalSamples,
                          autoStopOn,
                          downsampleRatio,
                          ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'],
                          sizeOfOneBuffer)
  assert_pico_ok(status["runStreaming"])

runStreaming()

actualSampleInterval = sampleInterval.value
actualSampleIntervalNs = actualSampleInterval

print(("Capturing at sample interval %s ns" % actualSampleIntervalNs))

# We need a big buffer, not registered with the driver, to keep our complete capture in.
bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
nextSample = 0
autoStopOuter = False
wasCalledBack = False

triggerLatch = False

def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
  if triggered == 1:
    global triggerLatch
    triggerLatch = True
  if triggerLatch is False:
    return
  global nextSample, autoStopOuter, wasCalledBack
  if autoStopOuter is True:
    return
  wasCalledBack = True
  destEnd = nextSample + noOfSamples
  sourceEnd = startIndex + noOfSamples
  bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
  nextSample += noOfSamples
  if autoStop:
    autoStopOuter = True

# Convert the python function into a C function pointer.
cFuncPtr = ps.StreamingReadyType(streaming_callback)

savecount = 0

while savecount < 15:
  while nextSample < totalSamples and not autoStopOuter:
    wasCalledBack = False
    # print("Calling back")
    status["getStreamingLastestValues"] = ps.ps2000aGetStreamingLatestValues(chandle, cFuncPtr, None)
    if not wasCalledBack:
      time.sleep(0.01)
  print("Flushing to disk..")
  np.save("/tmp/blonk-%d.npy" % savecount,bufferCompleteA)
  print("Flushed to disk..")
  savecount += 1
  # status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 0, int(mV2adc(10,channel_range,maxADC)), 2, 0, 0)
  runStreaming()
  triggerLatch = False  
  nextSample = 0
  autoStopOuter = False

print("Done grabbing values.")

# Convert ADC counts data to mV
adc2mVChAMax = adc2mV(bufferCompleteA, channel_range, maxADC)

# Create time data
time = np.linspace(0, (totalSamples) * actualSampleIntervalNs, totalSamples)
# Plot data from channel A and B
plt.plot(time, adc2mVChAMax[:])
# plt.plot(time,bufferCompleteA)
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.ylim(-25,25)
plt.show()

# Stop the scope
# handle = chandle
status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

# Disconnect the scope
# handle = chandle
status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

# Display status returns
print(status)
