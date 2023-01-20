import numpy as np
import csv
import torch
from torch.utils.data import Dataset


# order: [float V, float Aa, list(float) Pos,  float dt, list(float) Real Position]
def datacaller(filename):
    x = []
    y = []
    data = open(filename,newline='')
    reader = csv.reader(data, delimiter = ",")
    dataset = []
    for row in reader:
        dataset.append(row)
    for values in dataset:
        _temp2 = values[2].strip('][').split(',')
        _temp2[0] = float(_temp2[0])
        _temp2[1] = float(_temp2[1])
        _temp2[2] = float(_temp2[2])
        _temp4 = values[4].strip('][').split(',')
        _temp4[0] = float(_temp4[0])
        _temp4[1] = float(_temp4[1])
        
        _x= [float(values[0]), float(values[1]), float(_temp2[0]), float(_temp2[1]), float(_temp2[2]), float(values[3])]
        _y= [_temp4[0], _temp4[1]]
        
        x.append(_x)
        y.append(_y)
    data.close()
    
    return np.array(x),np.array(y)

class Data(Dataset):
    def __init__(self,x,y):
        self.x, self.y = x,y
        
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        x = self.x[idx]
        y = self.y[idx]
        return x,y