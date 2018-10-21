#!/usr/bin/python

from ds1054z import DS1054Z
import serial
import numpy as np

scope = DS1054Z("10.10.10.4")
scope.write(":STOP")
scope.write(":CHAN1:SCAL 0.02")
scope.write(":CHAN1:OFFS -0.055")
scope.write(":CHAN2:SCAL 5.0")
scope.write(":CHAN2:OFFS 0.0")
scope.write(":TRIG:MODE EDGE")
scope.write(":TRIG:EDGE:SOUR CHAN2")
scope.write(":TRIG:EDGE:LEV 2.0")
scope.write(":TRIG:EDGE:SWE SING")
scope.write(":WAV:SOUR CHAN1")
scope.single()
ser = serial.Serial('/dev/ttyUSB0',9600)
ser.write("e1122334455667788\n")
data = scope.get_waveform_samples("CHAN1",mode="RAW")
print len(data)
np.savez("lol.npz",traces=[data],data=[["lol"]],data_out=[["lol"]],freq=[250000000])
scope.close()
ser.close()
