"""
code, velocity, angular = sim.simxGetObjectVelocity(conn.id, car.pioneer, sim.simx_opmode_streaming)
count = 0.5
f = open('data.txt', 'w')

i = 0
t0 = 0
end_time = time.time() + count
car.Speed = 1
f.write("\n\n\n----forward----\n")
v1 = 0
t3 = time.time()
while t0 < end_time:
    code, velocity, angular = sim.simxGetObjectVelocity(conn.id, car.pioneer, sim.simx_opmode_buffer)
    v0 = math.sqrt((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))
    if v0 != v1:
        accel = (v0-v1)/(t0-t3)
        f.write("---------Acceleration---------\n")
        f.write(str(i)+" "+str(count+time.time()-end_time)+" "+str(t0-t3)+" "+str(accel)+"\n")
        f.write("------------------------------\n")
        t3 = time.time()
    t1 = time.time()
    if i%10 ==0:
        f.write(str(i)+" "+str(count+time.time()-end_time)+" "+str(v0)+"\n")
    t0 = t1
    i=i+1
    v1=v0


count = 1
i = 0
t0 = 0
end_time = time.time() + count
car.Speed = -1
f.write("\n\n\n\n\n\n----backward----\n")
while t0 < end_time:
    code, velocity, angular = sim.simxGetObjectVelocity(conn.id, car.pioneer, sim.simx_opmode_buffer)
    v0 = math.sqrt((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))
    if v0 != v1:
        accel = (v0-v1)/(t0-t3)
        f.write("---------Acceleration---------\n")
        f.write(str(i)+" "+str(count+time.time()-end_time)+" "+str(t0-t3)+" "+str(accel)+"\n")
        f.write("------------------------------\n")
        t3 = time.time()
    t1 = time.time()
    if i%10 ==0:
        f.write(str(i)+" "+str(count+time.time()-end_time)+" "+str(v0)+"\n")
    t0 = t1
    i=i+1
    v1=v0

count =0.5
i = 0
t0 = 0
end_time = time.time() + count
car.Speed = 0.0
f.write("\n\n\n\n\n\n----stop----\n")
while t0 < end_time:
    code, velocity, angular = sim.simxGetObjectVelocity(conn.id, car.pioneer, sim.simx_opmode_buffer)
    v0 = math.sqrt((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))
    if v0 != v1:
        accel = (v0-v1)/(t0-t3)
        f.write("---------Acceleration---------\n")
        f.write(str(i)+" "+str(count+time.time()-end_time)+" "+str(t0-t3)+" "+str(accel)+"\n")
        f.write("------------------------------\n")
        t3 = time.time()
    t1 = time.time()
    if i%10 ==0:
        f.write(str(i)+" "+str(count+time.time()-end_time)+" "+str(v0)+"\n")
    t0 = t1
    i=i+1
    v1=v0
"""