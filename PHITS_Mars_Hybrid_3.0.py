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

#############################################################################
#############################################################################
#                  Atmospheric Data (Interp/Extrap)  (Complete)
#############################################################################
#############################################################################
### Enter Special Conditions (INF, SUB, REG)
Condition = 'SUB'
### Enter amount of Wanted Data Points, upper, and lower bounds
#DP = int(math.ceil(float(raw_input('Input amount of data points :'))/0.61835))
Linefit = 1000000
Lower = -50000
Upper = 200000

#***********************************************
# Create Extrapolated Graph Based on Data
#***********************************************

inf=[]
info = []
height = []
density = []

#F = open('mars_gram.txt', 'r')
F = open('MCD.txt', 'r')
for i in F:
    inf.append(i)
for i in inf:
    info.append(i[:-1])
for i in range(2,int(info[0])+2):
    height.append(float(info[i]))
for i in range(int(info[0])+3,int(info[0])*2+3):
    density.append(float(info[i]))

### Calculate Altitudes Between Lowest and Highest Parts of Atmosphere
yval=[]
limit = Lower
while limit <= Upper:
    yval.append(limit)
    limit = limit + (Upper-Lower)/(Linefit)
    
### Get the X-Values for the Interpolated Data
xval=[]
# Extrapolate to -8km using point p (from first point) as interpolation start
j = 0
i=0
### Extrapolate
slope2 = (height[j+1]-height[j])/(math.log(density[j+1])-math.log(density[j]))
while yval[i] <= height[j]:
    ext2 = math.exp((yval[i]+(math.log(density[j])*slope2-height[j]))/(slope2))
    xval.append(ext2)
    i+=1
#print xval
### Interpolate Between Data
for i in yval:
    x2=0
    for j in range(0,int(info[0])-1):
        if i > height[j] and i < height[j+1]:
            x2 = math.exp(((i-height[j])*(math.log(density[j+1])-math.log(density[j]))/(height[j+1]-height[j])) + math.log(density[j]))
            xval.append(x2)

### Extrapolate to 200km using point p (from last point) as interpolation start
g = 0
i = len(xval)
k = len(height)-2 - g
### Extrapolate
slope = (height[k+1]-height[k])/(math.log(density[k+1])-math.log(density[k]))
for l in range(i,len(yval)):
        ext = math.exp((yval[l]+(math.log(density[k])*slope-height[k]))/(slope))
        xval.append(ext)
F.close()
      
#***************************************************
#              Interp/Extrap Data 
#***************************************************
if Condition == 'REG' or Condition == 'SUB':
    lowbound = -7152
elif Condition == 'INF':
    lowbound = -10000
Ulim = 120000
summ2=0
# Define a delta term for integration
delta = yval[1]-yval[0]

aerial_density=[]
cdf = []
### Total Aerial Density
for i in range(len(xval)-1, -1, -1):
    if yval[i] >= lowbound and yval[i]<=Ulim:
        summ2 = xval[i]*(delta)*0.1 + summ2
        aerial_density.append(summ2)
    
print 'The True Column Density is'    
print summ2

i=0
Column_Density=0
while yval[i] <= Ulim:  
    if yval[i] >= lowbound:
        Column_Density = Column_Density + delta*xval[i]/10
        i+=1
    else:
        i+=1
    if Column_Density >= np.ceil(0.87*summ2):
        break

#############################################################################
#############################################################################
#                  Atmospheric Data (Model) (Complete)
#############################################################################
#############################################################################

#***************************************************
#           Make Model Parameters
#***************************************************
highbound = yval[i]
step = 1.0
count = step
# Do a loop to find the density at the lower and upper height boundaries 
i=0
Column_Density = 0
xModel = []
yModel = []
itrack = []
# Column Density Based Discritization Alititude Values
while yval[i] <= highbound:
    if yval[i] >= lowbound and yval[i]<=highbound:
        Column_Density = Column_Density + delta*xval[i]/10
        if yval[i] == lowbound:
            yModel.append(yval[i])
            itrack.append(i)
        if round(Column_Density,3) == count:  
          yModel.append(yval[i])
          itrack.append(i)
          count += step
        i+=1
    else:
        i+=1
# Column Density Based Discritization Density Values 
for k in range(0,len(yModel)-1):
    yave = int(math.ceil(itrack[k+1]/2+itrack[k]/2))
    xModel.append(xval[yave])
    
# Altitude Based Discritization
j=i
step2 = 5000
alt = yval[j-1] + step2
while yval[j-1] <= Ulim:
    if yval[j] == alt:
        yModel.append(yval[j])
        alt = alt + step2
    if yval[j] == alt - step2/2:
        xModel.append(xval[j])
    j+=1

if len(xModel)==len(yModel):
    xModel = xModel[:-1]
    
### Correct for split regions built in t-cross
y_Model = []
for i in range(0,len(yModel)-1):
    y_Model.append(yModel[i])
    y_Model.append((yModel[i] + yModel[i+1])/2)
    
#***************************************************
#           Calculate Column Density
#***************************************************
summ4 = 0
Model_Density = []
for i in range(len(xModel)-1, -1,-1):
    summ4 = summ4 + xModel[i]* (yModel[i+1] - yModel[i])*0.1
    Model_Density.append(summ4)
Model_Density = Model_Density[::-1]

print 'The Model Total Column Density is'
print summ4

#**************************************************
#                      CDF
#**************************************************
summ = 0
ycdf = []
ran = []
### Actual
for i in range(0,len(xval)):
    if yval[i] >= lowbound and yval[i]<= Ulim:
        summ = (xval[i]*(Upper-Lower)/(Linefit))*0.1 + summ
        cdf.append(summ/summ2)
        ycdf.append(yval[i])
        ran.append(i)
aerial_density = aerial_density[::-1]

summ3 = 0
Modelcdf = []
### Model
for i in range(0,len(xModel)):
    summ3 = summ3 + xModel[i]* (yModel[i+1] - yModel[i])*0.1
    Modelcdf.append(summ3/(summ4))
    
#**************************************************
#             Column Density Error
#**************************************************
err = []
for j in range(0,len(xModel)):
    ct =0
    for i in ran:
        if yModel[j] == round(yval[i],2):
            err.append(abs(Model_Density[j]-aerial_density[ct])*100/(aerial_density[ct]))
            ct+=1
        else:
            ct+=1

        
###############################################################################
##############################################################################
#                       Plotting Atmospheric Data
##############################################################################
##############################################################################
#
##*****************************************************************************
##                        Density with Altitude
##*****************************************************************************
#plt.figure
#params = {'mathtext.default': 'regular' }          
#plt.figure(figsize = (15,10.5))
#plt.rcParams.update(params)
#
#plt.xlabel("Density (kg/$m^3$)",  fontname="Arial", fontsize=30)
#plt.xscale('log')
#plt.axis([1E-15,1,-50E3,200E3])
#plt.tick_params(which='major', length=15, labelsize=25)
#plt.tick_params(which='minor', length=7)
##grid(b=True, which='major', color='light grey', linestyle='-')
#plt.grid(True, which='minor', color='lightgrey', linestyle='-')
#plt.grid(True, which='major', color='dimgrey', linestyle='-')
#
#plt.ylabel('Height (m)', fontname="Arial", fontsize=30)
#plt.title ("Mars Climate Database",fontsize=30)
#plt.rc('font',family='Arial')
##plt.errorbar(phits_eve,phits_tave,yerr=phits_FError, linestyle="None",capsize=8)
##plt.errorbar(HZETRN_eave, HZETRN_Results,xerr=HZETRN_err, linestyle="None", ecolor='r', capsize=0)
#
#p1 = plt.plot(density, height, 'k-', label = 'Mars Climate Database', linewidth = 4)
#p2 = plt.plot(xval, yval, 'g-', label = 'Interp/Extrap', linewidth = 4)
#p3 = plt.step(xModel, yModel[1:], 'r-', label = 'Model', linewidth = 4, where='post')
#
#plt.legend(loc=1,prop={'size':20})
##******************************************************************************
#plt.figure
#params = {'mathtext.default': 'regular' }          
#plt.figure(figsize = (15,10.5))
#plt.rcParams.update(params)
#
#plt.xlabel("Density (kg/$m^3$)",  fontname="Arial", fontsize=30)
#plt.xscale('log')
#plt.axis([1E-3,0.1,-10E3,20E3])
#plt.tick_params(which='major', length=15, labelsize=25)
#plt.tick_params(which='minor', length=7)
##grid(b=True, which='major', color='light grey', linestyle='-')
#plt.grid(True, which='minor', color='lightgrey', linestyle='-')
#plt.grid(True, which='major', color='dimgrey', linestyle='-')
#
#plt.ylabel('Height (m)', fontname="Arial", fontsize=30)
#plt.title ("Mars Climate Database",fontsize=30)
#plt.rc('font',family='Arial')
##plt.errorbar(phits_eve,phits_tave,yerr=phits_FError, linestyle="None",capsize=8)
##plt.errorbar(HZETRN_eave, HZETRN_Results,xerr=HZETRN_err, linestyle="None", ecolor='r', capsize=0)
#
#p1 = plt.plot(density, height, 'k-', label = 'Mars Climate Database', linewidth = 4)
#p2 = plt.plot(xval, yval, 'g-', label = 'Interp/Extrap', linewidth = 4)
#p3 = plt.step(xModel, yModel[1:], 'r-', label = 'Model', linewidth = 4, where='post')
#
#plt.legend(loc=1,prop={'size':20})
#
###****************************************************************************
###                               CDF
###****************************************************************************
#plt.figure
#params = {'mathtext.default': 'regular' }          
#plt.figure(figsize = (15,10.5))
#plt.rcParams.update(params)
#
#plt.xlabel("Altitude (m)",  fontname="Arial", fontsize=30)
##plt.xscale('log')
##plt.axis([-10000,200000,0,1.2])
#plt.tick_params(which='major', length=15, labelsize=25)
#plt.tick_params(which='minor', length=7)
##grid(b=True, which='major', color='light grey', linestyle='-')
#plt.grid(True, which='minor', color='lightgrey', linestyle='-')
#plt.grid(True, which='major', color='dimgrey', linestyle='-')
#
#plt.title ("CDF",fontsize=30)
#plt.rc('font',family='Arial')
#
#p1 = plt.plot(ycdf, cdf, 'b-', label = 'CDF Actual', linewidth = 4)
#p2 = plt.plot(yModel[1:], Modelcdf, 'r-', label = 'CDF Model', linewidth = 4)
#
#plt.legend(loc=1,prop={'size':20})
#plt.show()
#
###*****************************************************************************
###                           Aerial Density
###*****************************************************************************
#plt.figure
#params = {'mathtext.default': 'regular' }          
#plt.figure(figsize = (15,10.5))
#plt.rcParams.update(params)
#
#plt.xlabel("Altitude (m)",  fontname="Arial", fontsize=30)
##plt.xscale('log')
#plt.axis([-10000,120000,0,25])
#plt.tick_params(which='major', length=15, labelsize=25)
#plt.tick_params(which='minor', length=7)
##grid(b=True, which='major', color='light grey', linestyle='-')
#plt.grid(True, which='minor', color='lightgrey', linestyle='-')
#plt.grid(True, which='major', color='dimgrey', linestyle='-')
#
#plt.ylabel("Aerial Density (g/$cm^2$)",  fontname="Arial", fontsize=30)
#plt.title ("Aerial Density with Altitude",fontsize=30)
#plt.rc('font',family='Arial')
#
#p1 = plt.plot(ycdf, aerial_density, 'b-', label = 'Aerial Density (Actual)', linewidth = 4)
#p2 = plt.plot(yModel[1:], Model_Density, 'r-', label = 'Aerial Density (Model)', linewidth = 4)
#
#plt.legend(loc=1,prop={'size':20})
#plt.show()
#
##### Print the results for column density for total and at Gale Crater
##print 'Total Column Density'
##print summ2
##print 'Gale Column Density'
##print aerial_density[1] + (1/10)*(aerial_density[0]-aerial_density[1])
#
###*****************************************************************************
###                    Aerial Density Relative Error
###*****************************************************************************
#plt.figure
#params = {'mathtext.default': 'regular' }          
#plt.figure(figsize = (15,10.5))
#plt.rcParams.update(params)
#
#plt.xlabel("Altitude (m)",  fontname="Arial", fontsize=30)
#plt.tick_params(which='major', length=15, labelsize=25)
#plt.tick_params(which='minor', length=7)
##grid(b=True, which='major', color='light grey', linestyle='-')
#plt.grid(True, which='minor', color='lightgrey', linestyle='-')
#plt.grid(True, which='major', color='dimgrey', linestyle='-')
#
#plt.ylabel("Relative Error (%)",  fontname="Arial", fontsize=30)
#plt.title ("Aerial Density with Altitude",fontsize=30)
#plt.rc('font',family='Arial')
#
#p2 = plt.plot(yModel[2:], err[1:], 'b-', label = 'Relative Error', linewidth = 4)
#
#plt.legend(loc=1,prop={'size':20})
#plt.show()

#############################################################################
#############################################################################
#                      Create Cell and Surface Cards  (Complete)
#############################################################################
#############################################################################

### Specify the Regolith Radius to the Datum
regolith = 338950000.0
### Define Final terms that take into account the height from regolith, cm conversion, and neat densities
yFinal = []
xFinal = []   
#*************************************************
#               Subterrain Option
#*************************************************
sub = 0
den = 1.7
reg_surface = []
den_correction = []
### Enter wanted grams/cm**2 for SUB
gcm = 85
### Wanted depth in cm
depth = 1000
if Condition == 'SUB':
    for l in range(1,int(round(depth/(gcm/den),2)+1)):
        reg_surface.append((-gcm/(den*100)*l+yModel[0]))
        den_correction.append(den)
    sub = len(reg_surface)
    yModel = reg_surface[::-1] +y_Model 
    
#*************************************************
#      Scientific Notation and Unit Correction
#*************************************************
for i in range(0, len(yModel)):
    yFinal.append(yModel[i]*100+regolith)
for i in range(0, len(xModel)):
    if 'e' in str(xModel[i]):
        a = str(xModel[i])[:11] + 'E' + str(xModel[i])[-3:] 
    else: 
        c = str("{:.9E}".format(Decimal(xModel[i])))
        a = c[:11] + 'E-0' + c[-1:]
    xFinal.append(a)
    xFinal.append(a)
if Condition == 'SUB':
    xFinal = den_correction + xFinal 

#*************************************************
#          Create the Cell and Surfaces
#*************************************************
counter = 0
endnum=[]
plus1=0
if Condition == 'REG': regt = 175
elif Condition == 'INF': plus1 = 1
### Open the Template and Search for Flags
while yFinal[counter+sub] <= regolith + 25000:
    File = open('PHITS_Template.dat', 'r')
    read = File.readlines()
    newfile = []
    count = counter
    for i in read:
        if 'FLAG1' in i:
            ### Make Surface Cards
            if Condition == 'REG':
                newfile.append(str(9998-len(yFinal)+counter) + '        ' + 'so' + '            ' + str(yFinal[counter]-regt) + '\n')
            elif Condition == 'SUB':
                newfile.append(str(9998-len(yFinal)+counter) + '        ' + 'so' + '            ' + str(yFinal[counter]-10) + '\n')
            for j in range(9999-len(yFinal)+counter,9999):
                newfile.append(str(j) + '        ' + 'so' + '            ' + str(yFinal[count]) + '\n')
                count+=1
            newfile.append('9999' + '        ' + 'so' + '            ' + str(np.ceil(yFinal[len(yFinal)-1] * 2**(0.5))+50) + '\n')

        elif 'FLAG2' in i:
            ### Make Cell Cards
            count = 9999-len(yFinal)+counter
            newfile.append('1  -1  '+ '     ' + str(-(count-1+plus1)) + '\n')
            if Condition == 'REG' or Condition == 'SUB':
                newfile.append('2   2  ' + str(-1.7) + '  ' + str((count-1)) +  '  ' + str(-(count)) + '\n')
            for j in range(3,len(xFinal)+3-counter-1):
                if j-1 < 9 + plus1:
                    if xFinal[j-3] == 1.7:
                        newfile.append(str(j-plus1) + '   2  ' + '-' + str(xFinal[j-2]) + '  ' + str(count) + '  ' + str(-(count+1)) + '\n')    
                    else:
                        newfile.append(str(j-plus1) + '   1  ' + '-' + str(xFinal[j-2]) + '  ' + str(count) + '  ' + str(-(count+1)) + '\n')    
                    count+=1
                else:
                    if xFinal[j-5] == 1.7:
                        newfile.append(str(j-plus1) + '  2  ' + '-' + str(xFinal[j-4]) + '  ' + str(count) + '  ' + str(-(count+1)) + '\n')    
                    else:
                        newfile.append(str(j-plus1) + '  1  ' + '-' + str(xFinal[j-4]) + '  ' + str(count) + '  ' + str(-(count+1)) + '\n')    
                    count+=1
            newfile.append(str(j+1-plus1) + '  0     ' + str((count)) + '  ' + str(-(count+1)) + '\n')
            newfile.append(str(j+2-plus1) + ' -1       ' + str((count+1)) + '\n')
            endnum.append(j)
        else:
            newfile.append(i)
    
    ### Make a new Template with the Updated Geometry
    final = open('PHITS_Template_' + str(Condition) + '_' + str(counter) + '.dat', 'w')
    for i in newfile:
        final.write(i)
    final.close()
    counter += 1
    File.close()
    if Condition == 'INF': break

#############################################################################
#############################################################################
#                         Volume Editor    (Complete)
#############################################################################
#############################################################################

for q in range(0,counter):
    File = open('PHITS_Template_' + str(Condition) + '_' + str(q) + '.dat', 'r+')
    read = File.readlines()
    newfile = []
    count = 1
    for i in read:
#        if 'FLAG5' in i:
#            for j in range(0,len(xModel)-q):
#                ### Make Volume Constants
#                newfile.append('set: ' + 'c' + str(count) + '[(4/3)*pi*(' + str(yFinal[q+j+1]) + '**3' + str(-yFinal[q+j]) + '**3' + ')]' + '\n')
#                count += 1
        if 'FLAG6' in i:
            for k in range(0,len(xFinal)-q-1):
                if k+3 < 10 +plus1:
                    newfile.append( str(k+3-plus1) + '     ' + '[(4/3)*pi*(' + str(yFinal[q+k+1]) + '**3' + str(-yFinal[q+k]) + '**3' + ')]' + '\n')
                else:
                    newfile.append( str(k+3-plus1) + '    ' + '[(4/3)*pi*(' + str(yFinal[q+k+1]) + '**3' + str(-yFinal[q+k]) + '**3' + ')]' + '\n')
            newfile.append(str(k+3-plus1+1) + '    [(4/3)*pi*(350500675.0**3-350250675.0**3)]' + '\n')
        else:
            newfile.append(i)
    final = open('PHITS_Template_' + str(Condition) + '_' + str(q) + '.dat', 'w')
    for i in newfile:
        final.write(i)
    final.close()
    File.close()
    
    
#############################################################################
#############################################################################
#                         T-deposit & T-track    (incomplete)
#############################################################################
#############################################################################

### Open the file once more
for w in range(0,counter):
    File = open('PHITS_Template_' + str(Condition) + '_' + str(w) + '.dat', 'r')
    read = File.readlines()
    newfile = []
    for i in read:
### Make the definition for the regions (reg)
        if 'FLAG7' in i:
            if int(math.floor(k+3-plus1+1))%2 ==0:
                a = re.sub('FLAG7', 'reg = ' + str(int(math.floor(k+3-plus1+1))) , str(i))
            else:
                a = re.sub('FLAG7', 'reg = ' + str(int(math.floor(k+3-plus1))) , str(i))
            newfile.append(a)
        elif 'FLAG8' in i:
            for p in range(3,int(math.floor(k+3-plus1+1)/2)+3):
                a = re.sub('FLAG8', '  ' + str(p) + '      ' + str(p+1) + '     (4*pi*' + str(yFinal[w+p-2]) + '**2)', str(i))
                b =  '  ' + str(p+1) + '      ' + str(p) + '     (4*pi*' + str(yFinal[w+p-2]) + '**2)'
                newfile.append(a)          
                newfile.append(b + '\n')
        else: 
            newfile.append(i)
    final = open('PHITS_Template_' + str(Condition) + '_' + str(w) + '.dat', 'w')
    for i in newfile:
        final.write(i)
    final.close()
File.close()   

#############################################################################
#############################################################################
#                         Discrete Energy Editor    (COMPLETE)
#############################################################################
#############################################################################

### Wanted Energies
j = np.logspace(0, 5, 50)
### Edit Template2 to Discritize Energies
for q in range(0,counter):
    File = open('PHITS_Template_' + str(Condition) + '_' + str(q) + '.dat', 'r')
    read = File.readlines()
    count=0
    for z in range(0,len(j)):
        newfile = []
        for i in read:
            # Flag to change the energy to discritize
            if 'FLAG3' in i:
                a = re.sub('FLAG3', str(j[z]), str(i)).rstrip()
                newfile.append(str(a) + '\n')
            # Flag to change the source plane 
            elif 'FLAG4' in i:
                c = re.sub('FLAG4', str(yFinal[len(yFinal)-1]), str(i)).rstrip()
                newfile.append(str(c) + '\n')
            else:
                newfile.append(i)
        ### Make Path to Files
        if not os.path.exists('Mars_Files_' + str(Condition) + '_' + str(q)):
            os.makedirs('Mars_Files_' + str(Condition) + '_' + str(q))
        if not os.path.exists('Mars_Files_' + str(Condition) + '_' + str(q) + '/Mars_'+ str(Condition) + '_' + str(count)):
            os.makedirs('Mars_Files_' + str(Condition) + '_' + str(q) + '/Mars_'+ str(Condition) + '_' + str(count))
        ### Write New Files
        final = open('Mars_Files_' + str(Condition) + '_' + str(q) + '/Mars_'+ str(Condition) + '_' + str(count) + '/' + 'Mars' + '.dat', 'w')
        for y in newfile:
            final.write(y)
        final.close()
        count +=1
    File.close()
    
#############################################################################
#############################################################################
#                 phits_bash.sh and phits.in files    (Complete)
#############################################################################
#############################################################################    

### Open the file once more
for w in range(0,counter):
    for z in range(0,len(j)):
        shutil.copy('phits.in', 'Mars_Files_' + str(Condition) + '_' + str(w) + '/Mars_'+ str(Condition) + '_' + str(z) + '/phits.in')
        shutil.copy('phits_bash.sh', 'Mars_Files_' + str(Condition) + '_' + str(w) + '/Mars_'+ str(Condition) + '_' + str(z) + '/phits_bash.sh')
    
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#### Clean up the Folder
#for q in range(0,counter):
#    os.remove('PHITS_Template_' + str(Condition) + '_' + str(q) + '.dat')

print 'DONE'

t = time.time() - t
print("Elapsed time: %.6e" % t) 
