#!/usr/bin/python3

import chipwhisperer as cw
import chipwhisperer.analyzer as cwa
import sys
import getopt

proj = cw.open_project(sys.argv[1])
print("Project loaded...")
attack = cwa.cpa(proj,cwa.leakage_models.sbox_output)
attack.points_range = [75483,75483+33206]
print("Begin CPA job")
results = attack.run()
print(results.find_maximums())
print(results.best_guesses())
