#        Python Settings
from __future__ import division
from decimal import Decimal
import numpy as np
import re
import matplotlib.pyplot as plt
import math
import os
import shutil
import time

# Time
t = time.time()
direc = 'Mars_Files_SUB_0/Mars_SUB_34/'
# Output File Name
File = open(direc + 'flux_results_proton_neutron.dat','r').readlines()
newfile=[]
for i, line in enumerate(File):
    if '#  num     area           a-curr    r.err      a-curr    r.err ' in line:
        for j in range(1,199):
            newfile.append(File[i+j])
final = open(direc + 'Proton_Neutron_Results.txt', 'w')
for y in newfile:
    final.write(y)
final.close()

File2=open(direc + 'Proton_Neutron_Results.txt','r')
for i in File2:
    if float(i[24:35]) or float(i[45:56]) != 0:
        print str(i[45:56])
File2.close()

t = time.time() - t
print t