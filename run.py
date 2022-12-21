'''
Important:
speed variation of P3DX is about 1m/s² for up to 0.5m/s
(that is, 0.1m/s per second accelerating)
so if you want a speed of 0.5m/s it takes about 0.5s to acheave it from zero
and 1s to acheave it from -0.5m/s
while the speed function does not account for this, you can call a sleep or count
function to remind you of the time it takes to get to that speed by calling
the variable obj.operationtime after the speed function.

nota: o valor real da aceleração tende a uma parábola e portanto é dificil definir
o tempo que leva para levar o carro do repouso a velocidade final, portanto uma estimativa é usada
t=v [segundos]
'''
import sys
import time
from P3DX import P3DX
from simulator import sim
from simulator import SimConnection
from math import pi
from RSS import RSS
import threading as th

"""

A fazer:
start: data = [tempo, velocidade escalar, aceleração angular, posição RSS], answer = posição real
getPosition (P3DX)
getSpeed (P3DX)
separateSpeed
Calc accel
update

"""
tref = time.time()
P  = {}
V  = []
A = []
t = []
def speedcaler(freq):
    '''
    Devem existir as listas globais V (velocidade) e A (aceleração)
    deve ser passada a frequëncia de pulling do sensor de velocidade
    (exemplo: 60hz, 80hz, 100hz, não é recomendado o uso de mais que 100hz)
    '''
    tref = time.time()
    t.append(t0)
    T = 1/freq
    t0 = tref
    v0 = 0
    while True:
        v1 = car.getVelocity()
        t1 = time.time()
        if t1-t0 == 0:
            dt = 0.01
        else:
            dt = t1-t0
        accel = (v1-v0)/(dt)
        V.append(v1)
        A.append(accel)
        t.append(t1)
        t0 = t1
        time.sleep((T)-(time.time()-tref)%T)
        

            
        
    

    

#start
if __name__ == '__main__':
    conn = SimConnection()
    if conn.id == -1:
        sys.exit("Could not connect.")
    error_code, ping = sim.simxGetPingTime(conn.id)
    ping = ping/1000
    print("Running with ping of " + str(ping) + " s.")
    print("-------------------------------")
    #create objects
    tref = time.time()
    car = P3DX(connectionID=conn.id)
    finder = RSS(conn.id)

    
#só roda se a conexão for realizada.
car.Speed = 0.5
time.sleep(car.operationtime)
time.sleep(1-car.operationtime)
car.Speed = 0
time.sleep(car.operationtime)
x, y =finder.ReadSensor()
print(x, y)





#Encerra a conexão
print("-------------------------------")
print('closing connection')
time.sleep(0.25) #tempo para garantir o envio do ultimo comando
conn.close() #encerra a conexão com o simulador










