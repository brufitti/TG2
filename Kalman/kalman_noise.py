import torch 
import numpy as np
import csv


def noise_maker(data, amp, aditive=0, returntype = 0):
    
    """Makes a random gaussian noise on top of data values given in data tensor.
    
    Args:
        data (1D Tensor): data vector to multiply by the noise
        amp (float): Amplitude of the noise/std of the gaussian curve
        aditive (float): Amplitude of the aditive ambient noise
    """
    num_points = data.size(0)
    mean = torch.ones(num_points)
    std = torch.ones(num_points)*amp
    aditive_noise = torch.ones(num_points)*aditive
    zeros = torch.zeros(num_points)
    xn = torch.normal(mean,std)
    x0 = torch.normal(zeros, aditive_noise)
    if returntype == 0:
        return data*xn +x0
    else:
        return data*xn +x0, x0
#needs to make it usable for 2D tensors

def add_noise(x):
    """_Given a tensor with 6 valus, adds noise to the first 5 values and return a
    tensor of same shape.
    Must have noise_maker function

    Args:
        x (2D Tensor): Tensor of tensors to add noise, also known as your data.

    Returns:
        tensor: returns noisy data, notice that the 3rd, 4th and 5th elements are distances derived
        from RSS signals, therefore they are increassed by 5% to simulate loss by ambient impedance
        along with regular noise.
    """
    # order: [float Vel, float Aa, float dist1, float dist2, float dists3,  float dt]
    # Vector num_pointsx6x1->num_vectors 6x1
    new_data_series = torch.empty(0)
    new_values = torch.tensor([0])
    
    for values in x:
        Vel,Aa,d1,d2,d3,dt = values[0].view(1),values[1].view(1),values[2].view(1),values[3].view(1),values[4].view(1),values[5].view(1)
        Vel = noise_maker(Vel, 0.06/3)
        Aa = noise_maker(Aa, 0.02/3)
        d1 = noise_maker(d1*1.05, 0.05/3)
        d2 = noise_maker(d2*1.05, 0.05/3)
        d3 = noise_maker(d3*1.05, 0.05/3)
        new_values = torch.cat((Vel,Aa,d1,d2,d3,dt),0)
        new_data_series = torch.cat((new_data_series,new_values),0)
    new_x = new_data_series.reshape(-1,6)
    return new_x



def filecaller():
    filename = []
    savefiles = []
    for speedtxt in range(3,6):
        for degrees in range (0,300,60):
            name = "data/data-{degree}-0{speeddecimal}mps.csv".format(degree = degrees, speeddecimal = speedtxt)
            savename = "data/noisy-data-{degree}-0{speeddecimal}mps.csv".format(degree = degrees, speeddecimal = speedtxt)
            filename.append(name)
            savefiles.append(savename)
    return filename, savefiles

def datacaller(name):
    x = []
    y = []
    data = open(name,newline='')
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
    
if __name__ == "__main__":
    #Creates noisy files to be used in Kalman
    filename, savefiles = filecaller()
    for idx, name in enumerate(filename):
        savefile = savefiles[idx]
        writer = csv.writer(open(savefile, 'w', newline=''))
        x,y = datacaller(name)
        # new_x = x
        new_x = add_noise(torch.tensor(x))
        new_x = new_x.numpy()
        for idx2, values in enumerate(new_x):
            text = [values[0],values[1],values[2],values[3],values[4],values[5],y[idx2][0],y[idx2][1]]
            writer.writerow(text)
