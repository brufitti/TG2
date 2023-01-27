import csv
import numpy as np

def filecaller():
    filename = []
    for speedtxt in range(3,6):
        for degrees in range (0,300,60):
            filename.append("Kalman/tests\kalman-tests{degree}{speeddecimal}.csv".format(degree = degrees, speeddecimal = speedtxt))
    return filename

def datacaller(filename):
    real, tri_xy, dif_tri, vel_xy, dif_vel = [],[],[],[],[]
    data = open(filename,newline='')
    reader = csv.reader(data, delimiter = ",")
    
    dataset = []
    for row in reader:
        dataset.append(row)
    
    for data in dataset:
        _real, _tri_xy, _dif_tri, _vel_xy, _dif_vel = data
        real.append(_real)
        tri_xy.append(_tri_xy)
        dif_tri.append(_dif_tri.strip(']['))
        vel_xy.append(_vel_xy)
        dif_vel.append(_dif_vel.strip(']['))
   
    return dif_tri, dif_vel

if __name__ == "__main__":
    filename = filecaller()
    data = []
    tri_errorsx, tri_errorsy = [],[]
    vel_errorsx, vel_errorsy = [],[]
    for name in filename:
        dif_tri, dif_vel = datacaller(name)
        for value in dif_tri:
            import pdb;pdb.set_trace()
            tri_errorsx.append(float(value[0].strip(']').strip('[').strip('\'')))
            tri_errorsy.append(float(value[1]))
        for value in dif_vel:
            vel_errorsx.append(float(value[0]))
            vel_errorsy.append(float(value[1]))
            
    len_tri = len(tri_errorsx)
    len_vel = len(vel_errorsx)
    var_trix = np.sum(np.power(tri_errorsx,2))/(len_tri-1)
    var_triy = np.sum(np.power(tri_errorsy,2))/(len_tri-1)
    var_velx = np.sum(np.power(vel_errorsx,2))/(vel_tri-1)
    var_vely = np.sum(np.power(vel_errorsy,2))/(vel_tri-1)

    print(var_trix, var_triy)
    print(var_velx, var_vely)