# Side Channels 'n' Stuff

![Just for fun](fun/cap.png)

The fuckshitfuck toolkit is a repository of code used for side channel acquisition, preprocessing and analysis, similar to the ChipWhisperer, but written ground-up as an (extremely successful) learning exercise.

This toolkit comprises:

- Acquisition:
  - ./grab3.py, for acquisition from picoscope scopes
  - ./rigol-new.py, for acquisition from rigol scopes
  - ./x/fuck.py, for pcsc+picoscope acquisition from smartcards
- Preprocessing:
  - ./preprocessor.py, for temporal alignment of traces
- Analysis:
  - ./cpa.py, a multi-model tool for correlation analysis
  - ./dpa.py, a multi-model tool for differential analysis
  - ./plot.py, a simple matplotlib-based tool to view sets of traces

Note the correlation and differential analysis front-ends are now decoupled from the leakage modelling back-ends - models can be found in support/attack.py. cpa.py and dpa.py typically do not need to be changed to analyze traces using different leakage hypotheses.

Some test targets are provided in target/ and pictarget-3.X/

The code is provided as-is, pull requests and feature requests are welcome.
