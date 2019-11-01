# Keyboard Tools

![Just for fun](../fun/keypress-cropped.png)

This sub-toolkit is for capturing the EM emissions from a keyboard, similar to the work of Martin Vuagnoux and Sylvaini Pasini (see: lasecwww.epfl.ch/keyboard), and further expanded on in "SoK: Keylogging Side Channels" (see: ieeexplore.ieee.org/document/8418605).

Note that we do not rely on delay - instead, we rely on the shape and duration of electromagnetic emissions.

This directory uses dual channel measurement by default, to improve the accuracy of any correlation attacks.

Note that support.py holds a unified data preprocessing function, so what you plot is the data the actual analysis is done against (i.e. use support.block_preprocess_function)
