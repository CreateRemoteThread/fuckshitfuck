# capturebuddy

## introduction

capturebuddy is a python script to provide a near-universal api for side channel
analysis. to use it to capture LTE authentication via a rigol scope, configure
rigol.py with your scope's IP Address (look for CaptureInterface) and run:

./capturebuddy.py -a rigol -d scard

then, at the command prompt, hit "run" for 5 captures into <uuid>.traces and uuid.data/

## extending

new acqusition frontends and control drivers can be implemented by copying test.py
in the frontends/ and drivers/ folders. make sure that your implemented functions
return data in the expected format, and that arm behaves appropriately, the test
stubs implement non-functional examples.
