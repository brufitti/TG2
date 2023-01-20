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
from time import time, sleep, localtime
from P3DX import P3DX
from simulator import sim
from simulator import SimConnection
from math import pi, sqrt
from RSS import RSS
import threading as th
import queue
import csv

"""

A fazer:
start: data = [tempo, velocidade escalar, aceleração angular, posição RSS], answer = posição real
getPosition (P3DX)
getSpeed (P3DX)
separateSpeed
Calc accel
update

"""

# Global stuff
V  = queue.Queue()
Aa = queue.Queue()
t = queue.Queue()

def get_all(queue):
    list = []
    counter = 0 
    while not queue.empty():
        list.append(queue.get())
    return list

def speedCaller(freq, car, breaker):
    '''
    Devem existir as listas globais V (velocidade) e Aa (aceleração angular).
    Deve ser passada a frequëncia de pulling do sensor de velocidade
    (exemplo: 60hz, 80hz, 100hz, não é recomendado o uso de mais que 100hz)
    '''
    sleep(0.1)
    tref = time()
    T, t0, o0 = 1/freq, tref, 0
    global V, Aa, t
    while 1:
        velocity = car.getVelocity()
        vel = sqrt((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))
        V.put(vel)
        o1 = velocity[3]
        t1 = time()
        if t1-t0 != 0:
            dt = t1-t0
        else:
            dt = T
        Aa.put((o1-o0)/(dt))
        o0= o1
        t0 = t1
        sleep((T)-(time()-tref)%T)
        if breaker.is_set():
            break

        
        
def dataCaller(freq, finder, car, writer, breaker):
    '''
    Devem existir as variáveis globais t (tempo de aglutinação), V (velocidade),
    Aa (aceleração Angular) e a lista P (posição pelo RSS).
    Deve ser passada a frequência de aglutinação dos dados.
    '''
    t0 = time()
    T = 1/freq
    tref = t0
    i = 1
    global V, Aa, t, data
    Vlist = [0]
    Aalist = [0]
    while 1:
        sleep(0.1)
        test = True
        PosR = car.getPosition()
        if ((not V.empty()) and (not Aa.empty())):
            if test == True:
                Vlist = get_all(V)
                Aalist = get_all(Aa)
                test = False
            else:
                Aalist = get_all(V)
                Vlist = get_all(Aa)
                test = True  
        Vi = sum(Vlist)/len(Vlist)
        Aai = sum(Aalist)/len(Aalist)
        Pos = finder() # objeto RSS __call__
        t1 = time()
        text = [Vi, Aai, Pos, t1-t0, PosR]
        writer.writerow(text) # "Velocidade | aceleração angular | Posição (RSS) | time | Posição real\n"
        t0 = t1
        sleep((T)-(time()-tref)%T)
        if breaker.is_set():
            break

        
    
# start
if __name__ == "__main__":
    
    conn = SimConnection()
    if conn.id == -1:
        sys.exit("Could not connect.")
    error_code, ping = sim.simxGetPingTime(conn.id)
    ping = ping/1000
    print("Running with ping of ", str(ping), " s.")
    print("-------------------------------")
    # create objects
    tref = time()
    car = P3DX(connectionID=conn.id)
    finder = RSS(conn.id)
    breaker = th.Event()
    for speedtxt in range(1,6):
        for degrees in range (0,300,60):
            if (speedtxt != 4) and (degrees != 60):
                continue
            speed = speedtxt/10
            print("-------New Batch-------")
            print("Speed ={sp}".format(sp = speed))
            print("Starting Angle ={ang}".format(ang = degrees))
            filename = "data-{degree}-0{speeddecimal}mps.csv".format(degree = degrees, speeddecimal=speedtxt)
            data = open(filename, 'w', newline='')
            writer = csv.writer(data)
            th1 = th.Thread(target = speedCaller, args=(100,car,breaker))
            th2 = th.Thread(target = dataCaller, args=(20,finder,car,writer, breaker))
            
            # da um pontapé no veículo para inicializar corretamente os sensores
            car.Speed = speed
            sleep(0.4)
            car.Speed = 0
            sleep(car.operationtime)
            
            # inicia as funções
            th1.start()
            th2.start()
            car.autopilot(speed, degrees)
            
            # para as threads
            breaker.set()
            # Espera tudo acabar, reseta o evento das threads e fecha o arquivo anterior
            sleep(2)
            data.close()
            breaker.clear()
            print("-------End of Batch-------")
    print("-------------------------------")
    print('closing connection')
    sleep(0.25) # tempo para garantir o envio do ultimo comando
    conn.close() # encerra a conexão com o simulador