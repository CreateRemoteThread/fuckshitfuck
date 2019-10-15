# Keyboard Tools

![Just for fun](../fun/keypress-cropped.png)

This sub-toolkit is for capturing the EM emissions from a keyboard for peak identification, as per the work of Martin Vuagnoux and Sylvaini Pasini (see: lasecwww.epfl.ch/keyboard), and further expanded on in "SoK: Keylogging Side Channels" (see: ieeexplore.ieee.org/document/8418605).

In summary, the scan matrix of a keyboard creates large electro-magnetic field spikes during an active scan cycle, and a keypress disrupts this process.

The "heavy lifting" algorithms are in support.py, a.py just acquires samples and offloads.
