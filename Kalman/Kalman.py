from Trilateration import trilateration
from AngularKinematics import calc_theta, calc_componnents
from math import sqrt
import csv
import numpy as np
import os

def filecaller():
    filename = []
    theta0, speed0 = [],[]
    for speedtxt in range(3,6):
        for degrees in range (0,300,60):
            filename.append("data/noisy-data-{degree}-0{speeddecimal}mps.csv".format(degree = degrees, speeddecimal = speedtxt))
            theta0.append(degrees)
            speed0.append(speedtxt)
            
    return filename, theta0, speed0

# order: [float V, float Aa, list(float) dists, float dt, list(float) Real Position]
def datacaller(filename):
    Vel,Aa,d1,d2,d3,dt,y = [],[],[],[],[],[],[]
    data = open(filename,newline='')
    reader = csv.reader(data, delimiter = ",")
    
    dataset = []
    for row in reader:
        dataset.append(row)
        
    for values in dataset:
        Vel.append(float(values[0]))
        Aa.append(float(values[1]))
        d1.append(float(values[2]))
        d2.append(float(values[3]))
        d3.append(float(values[4]))
        dt.append(float(values[5]))
        y.append([float(values[6]),float(values[7])])
        
    data.close()
    organized_data = [Vel,Aa,d1,d2,d3,dt]
    return organized_data,y, dt, Vel


def Position_speeds_calc(data,theta0):
    Vel,Aa,d1,d2,d3,dt=data # ~8k data points
    vel_xy = [],[]
    vel_x, vel_y = [],[]
    tri_xy = trilateration(d1,d2,d3)
    orientations = calc_theta(Aa,dt,theta0)
    
    for idx, vel_xy in enumerate(Vel):
        vel_xy = (calc_componnents(Vel[idx],orientations[idx]))
        vel_x.append(vel_xy[0])
        vel_y.append(vel_xy[1])
    
    return tri_xy, vel_x, vel_y

def kalman_predictor(val1, var, dt, vel, var_vel, cov = 0, noisevar = 0):
    pP2 = val1 + dt*(vel) # Predicted Position 2
    var2 = (var) + ((dt**2) * var_vel) + (2*dt*cov) + (dt*noisevar)
    return pP2, var2

def kalman_updater(predicted_P2, pvar2, measured_P2, var2):
    K = (pvar2)/((pvar2) + (var2))
    estimated_P2 = predicted_P2 + K*(measured_P2-predicted_P2)
    estimated_var2 = (pvar2) + K*(pvar2)
    return estimated_P2, estimated_var2

# Make a covariance function using numpy cov

if __name__ == "__main__":
    filename, theta0, speedtxt = filecaller()
    
    variances_x = 0
    variances_y = 0
    for idx, name in enumerate(filename):
        
        outfile = "Kalman/outputs/kalman-{degree}-0{speeddecimal}.csv".format(degree = theta0[idx], speeddecimal = speedtxt[idx])
        # os.remove(outfile)
        savefile = open(outfile, 'w', newline='')
        writer = csv.writer(savefile)
        
        organized_data, y, dt, Vel = datacaller(name)
        theta = theta0[idx]
        tri_xy, vel_x, vel_y = Position_speeds_calc(organized_data, theta)
        
        tri_x,tri_y = [],[]
        for pair in tri_xy:
            tri_x.append(pair[0])
            tri_y.append(pair[1])
        
        # Data acquired from experiment 1
        # var_vel_x = 0.024336645090730552
        # var_vel_y = 0.024124731596327650
        # var_tri_x = 0.0005897439032232617
        # var_tri_y = 0.00032263555854781693
        # Data acquired from experiment 2
        var_tri_x = 0.020139725240178142
        var_tri_y = 0.01788998730140539
        var_vel_x = 0.031589845726035863
        var_vel_y = 0.03024044885157414
        
        
        # uncomment this for var testing
        # var_test_predx, var_test_predy = [],[]
        
        # Kalman Prediction in x
        final_kalman_x = []
        for idx2, speed in enumerate(vel_x):
            combined_kalman_x = 0
            if idx2 == 0:
                combined_kalman_x = tri_x[idx2]
            else:
                combined_kalman_x, combined_var = kalman_updater(pred_x, pred_var_x, tri_x[idx], var_tri_x)
            final_kalman_x.append(combined_kalman_x)
            pred_x, pred_var_x = kalman_predictor(tri_x[idx2], var_tri_x, dt[idx2],speed, var_vel_x)
            # var_test_predx.append(pred_x)
           
        # Kalman Prediction in y
        final_kalman_y = []
        for idx2, speed in enumerate(vel_y):
            combined_kalman_y = 0
            if idx2 == 0:
                combined_kalman_y = tri_y[idx2]
            else:
                combined_kalman_y, combined_var = kalman_updater(pred_y, pred_var_y, tri_y[idx], var_tri_y)
            final_kalman_y.append(combined_kalman_y)
            pred_y, pred_var_y = kalman_predictor(tri_y[idx2], var_tri_y, dt[idx2],speed, var_vel_y)
            # var_test_predy.append(pred_y)
        MSE = 0
        for idx2, value in enumerate(y):
            dif = [value[0]-final_kalman_x[idx2], value[1]-final_kalman_y[idx2]]
            text = [value, [final_kalman_x[idx2], final_kalman_y[idx2]], dif]
            writer.writerow(text)
            MSE = ((dif[0]**2) + (dif[1]**2))
        MSE = MSE/len(y)
        text = [[MSE,MSE],[MSE,MSE],[MSE,MSE]]
        writer.writerow(text)
        
        
        
        
        # Estimatind the variance of trilateration values
    #     varx, vary = 0,0
    #     for idx, value in enumerate(tri_x):
    #         varx += (y[idx][0] - value)**2
    #     varx = varx/(len(tri_x)-1)
    #     variances_x += varx/15
        
    #     for idx, value in enumerate(tri_y):
    #         vary += (y[idx][1] - value)**2
    #     vary = vary/(len(tri_y)-1)
    #     variances_y += vary/15
    # print(variances_x)
    # print(variances_y)
        
        # Estimating the variance of predicted values
    #     varx, vary = 0,0
    #     for idx, values in enumerate(var_test_predx):
    #         varx += (y[idx][0]-values)**2
    #     varx = varx/(len(var_test_predx)-1)
    #     variances_x += varx/15
    #     for idx, values in enumerate(var_test_predy):
    #         vary += (y[idx][1]-values)**2
    #     vary = vary/(len(var_test_predy)-1)
    #     variances_y += vary/15
        
    # print(variances_x)
    # print(variances_y)