import numpy as np
import csv

data = open('results10kepoches.csv',newline='')
reader = csv.reader(data, delimiter = ",")
results = list()

def MSE(dif):
    
    for i in range(len(dif)):
        MSE = (a**2)-(b**2)
    
for step in reader:
    results.append(step)
# Shape real[x,y],|,pred[x,y],|,dif[x,y]
#           "[00,01]",1,[20,21],3,[40,41]

for data in results:
    _temp0 = data[0].split(',')
    _temp2 = data[2].split(',')
    _temp4 = data[4].split(',')
    _temp0 = [float(_temp0[0]),float(_temp0[1])]
    _temp2 = [float(_temp2[0]),float(_temp2[1])]
    _temp4 = [float(_temp4[0]),float(_temp4[1])]
    real = _temp0
    pred = _temp2
    dif = _temp4