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
from time import time, sleep
from P3DX import P3DX
from simulator import sim
from simulator import SimConnection
from math import pi
from RSS import RSS
import threading as th
import queue
"""

A fazer:
start: data = [tempo, velocidade escalar, aceleração angular, posição RSS], answer = posição real
getPosition (P3DX)
getSpeed (P3DX)
separateSpeed
Calc accel
update

"""

V  = queue.Queue()
Aa = queue.Queue()
t = queue.Queue()

def get_all(queue):
    list = []
    counter = 0 
    while not queue.empty():
        list.append(queue.get())
    return list

def speedCaller(freq, car):
    '''
    Devem existir as listas globais V (velocidade) e Aa (aceleração angular).
    Deve ser passada a frequëncia de pulling do sensor de velocidade
    (exemplo: 60hz, 80hz, 100hz, não é recomendado o uso de mais que 100hz)
    '''
    sleep(0.1)
    tref = time()
    T, t0, o0 = 1/freq, tref, 0
    global V, Aa, t
    for i in range(0, 1200*freq):
        vel = car.getVelocity()
        V.put(vel)
        o1 = car.getOrientation()
        t1 = time()
        if t1-t0 != 0:
            dt = t1-t0
        else:
            dt = 0.001
        Aa.put((o1-o0)/(dt))
        o0= o1
        t0 = t1
        sleep((T)-(time()-tref)%T)

        
        
def dataCaller(freq, finder, car):
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
    for i in range(0, 1200*freq):
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
        Pos = finder.ReadSensor()
        t1 = time()
        text = str(Vi)+" | "+str(Aai)+ " | " +str(Pos)+" | "+str(t1)+" | "+ str(PosR)+"\n"
        data.write(text)
        sleep((T)-(time()-tref)%T)

        
    
#start
if __name__ == "__main__":
    data = open("data.txt", "a")
    conn = SimConnection()
    if conn.id == -1:
        sys.exit("Could not connect.")
    error_code, ping = sim.simxGetPingTime(conn.id)
    ping = ping/1000
    print("Running with ping of " + str(ping) + " s.")
    print("-------------------------------")
    #create objects
    tref = time()
    car = P3DX(connectionID=conn.id)
    finder = RSS(conn.id)
    stopall = th.Event()
    data.write("New dataset\n")
    data.write("Velocidade | aceleração angular | Posição (RSS) | time | Posição real\n")
    th1 = th.Thread(target = speedCaller, args=(100,car,))
    th2 = th.Thread(target = dataCaller, args=(20,finder,car,))
    #da um pontapé no veículo para inicializar corretamente os sensores
    car.Speed = 0.3
    sleep(0.3)
    car.Speed = 0
    sleep(car.operationtime)
    #inicia as funções
    th1.start()
    th2.start()
    car.autopilot(0.3)
    
    #Encerra a conexão e fecha o arquivo
    data.close()
    print("-------------------------------")
    print('closing connection')
    sleep(0.25) #tempo para garantir o envio do ultimo comando
    conn.close() #encerra a conexão com o simulador