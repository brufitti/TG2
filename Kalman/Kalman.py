from Trilateration import trilateration
from AngularKinematics import calc_theta, calc_componnents
from math import sqrt
import csv
import numpy as np


def filecaller():
    filename = []
    theta0, speed0 = [],[]
    for speedtxt in range(3,6):
        for degrees in range (0,300,60):
            filename[i] = "data/data-{degree}-0{speeddecimal}mps.csv".format(degree = degrees, speeddecimal = speedtxt)
            theta0.append(degrees)
            speed0.append(speedtxt)
    return filename, theta0, speed0

# order: [float V, float Aa, list(float) dists, float dt, list(float) Real Position]
def datacaller(filename):
    Vel,Aa,d1,d2,d3,dt = [],[],[],[],[],[]
    data = open(filename,newline='')
    reader = csv.reader(data, delimiter = ",")
    
    dataset = []
    for row in reader:
        dataset.append(row)
        
    y = []
    for values in dataset:
        _temp2 = values[2].strip('][').split(',')
        _temp2[0] = float(_temp2[0])
        _temp2[1] = float(_temp2[1])
        _temp2[2] = float(_temp2[2])
        _temp4 = values[4].strip('][').split(',')
        _temp4[0] = float(_temp4[0])
        _temp4[1] = float(_temp4[1])

        Vel.append(float(values[0]))
        Aa.append(float(values[1]))
        d1.append(float(_temp2[0]))
        d2.append(float(_temp2[1]))
        d3.append(float(_temp2[2]))
        dt.append(float(values[3]))
        y.append([_temp4[0], _temp4[1]])
        
    data.close()
    organized_data = [Vel,Aa,d1,d2,d3,dt]
    return organized_data,y, dt


def Position(data,theta0,position0):
    Vel,Aa,d1,d2,d3,dt=data # ~8k data points
    ds, ds_componnents, vel_xy = [],[],[]
    vel_xy.append(position0)
    tri_xy = trilateration(d1,d2,d3)
    orientations = calc_theta(Aa,dt,theta0)
    
    for idx in range(len(Vel)):
        ds.append(Vel[idx]*dt[idx])
    
    for idx in range(len(ds)):
        ds_componnents.append(calc_componnents(ds[idx],orientations[idx]))
    _x,_y = position0[0], position0[1]
    
    for pair in ds_componnents:
        _dx,_dy = pair
        _x += _dx
        _y += _dy
        vel_xy.append([_x,_y])
    vel_xy.pop(-1)
    
    return tri_xy, vel_xy

def kalman_combinator(vala, stda, valb, stdb):
    
    valc = ( ((stdb**2) * vala) + ((stda**2) *valb) )/((stda**2)+(stdb**2))
    stdc = sqrt((( stda ** (-2) ) + ( stdb ** (-2) )) ** (-1))
    
    return valc, stdc

def kalman_predictor(val1, std, dt, vel, noise):
    pP2 = val1 + dt*(vel) # Predicted Position 2
    pstd2 = sqrt((std**2)  + dt * (noise**2))
    return pP2, pstd2

def kalman_updater(predicted_P2, pstd2, std, measured_P2):
    K = (pstd2**2)/((pstd2**2) + (std**2))
    estimated_P2 = predicted_P2 + K*(measured_P2-predicted_P2)
    estimated_std2 = sqrt((pstd2**2) + K*(pstd2**2))
    return estimated_P2, estimated_std2

# Make a covariance function using numpy cov

if __name__ == "__main__":
    filename, theta0, speedtxt = filecaller()
    tri_xy, vel_xy = [],[]
    #Pass noise function with returntype = 1
    for idx, name in enumerate(filename):
        import pdb; pdb.set_trace()
        savefile = open("Kalman/outputs/kalman-{degree}-0{speeddecimal}".format(degree = theta0[idx], speeddecimal = speedtxt[idx]), 'w', newline='')
        writer = csv.writer(savefile)
        
        organized_data, y, dt = datacaller(name)
        theta = theta0[idx]
        tri_xy, vel_xy = Position(organized_data, theta, y[0])
        tri_x,tri_y,vel_x,vel_y = [],[],[],[]
        
        for pair in tri_xy:
            tri_x.append(pair[0])
            tri_y.append(pair[1])
        
        for pair in vel_xy:
            vel_x.append(pair[0])
            vel_y.append(pair[1])
        # cov = np.cov([tri_x,vel_x])
        # cov_x = cov[0,1]
        # cov = np.cov([tri_y,vel_y])
        # cov_y = cov[0,1]
        # vel_var = 0.02
        # Aa_var = 0.02
        # dists_var = 0.05/3
        vel_xy_var = 0.02*(0.02)
        tri_xy_var = 0.05/3*(2/3) # Needs better analysis
        Px, Py, P_kalman = [],[],[]
        std = 0
        
        for time, value1 in enumerate(vel_x):
            value2 = tri_x[time]
            P, std = kalman_combinator(value1, vel_xy_var, value2, tri_xy_var)
            Px.append(P)
        
        for time, value1 in enumerate(vel_y):
            value2 = tri_y[time]
            P, std = kalman_combinator(value1, vel_xy_var, value2, tri_xy_var)
            Py.append(P)
        
        for idx, values_x in enumerate(Px):
            values_y = Py[idx]
            P_kalman.append([values_x, values_y])
        
        for idx, result in enumerate(P_kalman):
            real = y[idx]
            dif = np.subtract(real,result)
            text = [real, result, dif]
            writer.writerow(text)