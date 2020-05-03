# capturebuddy

## introduction

capturebuddy is a modular signal acquisition framework, building on the grab-* series of scripts in previous versions of this toolset. capturebuddy is a user interface for a "driver", controlling target IO, and a "fronend", acquiring a signal from an oscilloscope through a stable API.

to run capturebuddy, you *must* specify both, like this:

./capturebuddy -d uart -f rigol

to run a capture job, you can set a few variables (which are passed to both the driver and frontend):

set tracecount=500
set samplecount=10000
set writefile="/stuff/pew"
run

## triggerbuddy

triggerbuddy is the python control code for my fpga trigger mechanism. it can be invoked from within capturebuddy: the trigger can be instantiated (and passed to the driver/frontend) with "t". any commands coming after "t" are passed directly to triggerbuddy.

triggerbuddy supports the following commands:

- t io <io_edges>
- t clk <clk_edges>
- t arm (callable via trigger.arm())
- t disarm (callable via trigger.disarm())

the fpga project is meant for a digitlent Arty A7 board (35t variant), but it should be fairly simple to port this to any hardware.

## extending

you can implement new frontends and drivers by copying frontends/test.py and drivers/test.py. it's worth noting that it's ultimatly the driver's job to arm and initialize the scope (so you can decrease the total amount of "wait time" for your scope or triggering apparatus).
