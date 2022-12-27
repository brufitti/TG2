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
from math import pi, sqrt
from RSS import RSS
from multiprocessing import Process
import keyboard

def dataCaller(f1, f2, i, j, tref, car,V, Aa, do0, finder, data):
    """_summary_

    Args:
        f1 (int): frequência do sensor de velocidade, 40 a 100Hz, deve ser multiplo de f2.
        f2 (int): frequência do acumulador e RSS, 10 a 25Hz, deve ser uma fração inteira de f1.  
        i (int): iterador do loop externo
        tref (time.time()): instante em que a função foi chamada
        car (object: objeto carro
        V (list): velocidade linear
        Aa (list): Aceleração angular
        do0 (float): velocidade angular antes do loop externo (0)
        finder (object): objeto RSS 
        data (file): arquivo.txt
    """
    
    T, n, t0 = 1/f1, f1/f2, tref
    while 1:
        V.append(car.getVelocity(1))
        do1 = car.getVelocity(2)
        t1 = time()
        if t1-t0 != 0:
            dt = t1-t0
        else:
            dt = 0.001
        Aa.append((do1-do0)/(dt))
        do0= do1
        if i < n-1:
            i += 1
            sleep((T)-(time()-tref)%T)
        else:
            PosR = car.getPosition()
            Vi = sum(V)/len(V)
            Aai = sum(Aa)/len(Aa)
            Pos = finder.ReadSensor()
            t1 = time()
            txt = str(str(j) + " | " +  str(Aai) + " | " + str(Pos) + " | " + str(t1) + " | " + str(PosR) + "\n")
            data.write(txt)
            V.clear()
            Aa.clear()
            i = 0
            j += 1 
            sleep((T)-(time()-tref)%T)

def autopilot(car, speed, data, finder):

    tloop0 = time()
    tref = tloop0
    f1,f2,count1, count2, do0 = 100, 25, 0, 0, 0
    V = []
    Aa = []    
    prev_detect = [False, False, False, False]
    
    while 1:
        if keyboard.is_pressed('ctrl'):
            print("Saindo do piloto automático")
            car.Speed = 0
            sleep(car.operationtime)
            break
        detect = [False, False, False, False]
        #Lê a distância entre o carro e cada parede
        for i in range(0,4):
            err, car.distances[i] = sim.simxCheckDistance(car.connectionID, car.pioneer, car.walls[i], sim.simx_opmode_buffer)
        #detecta se precisa virar de alguma parede
        i = 0
        for dist in car.distances:
            if dist <= 0.65:
                detect[i] = True
            elif dist <= 0.4:
                car.ddrive(0, 180)
            i = i + 1
            car.Speed = speed
        #testa se precisa virar
        for i in range(0,4):
            if (detect[i] == True and detect[i] != prev_detect[i]):
                print("parede", i, "encontrada")
                err, angles = sim.simxGetObjectOrientation(car.connectionID, car.pioneer, car.walls[i], sim.simx_opmode_buffer)
                inangle = angles[2]*180/pi
                print("inangle: ", inangle)
                if (inangle >=-180 and inangle <= -90):
                    #para para entrar no modo curva
                    car.Speed = 0
                    toperation = time()
                    while time()-toperation < car.operationtime :
                        dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
                    #Turn 90º
                    car.ddrive(0, 90, waux=-pi/2)
                    toperation = time()
                    while time()-toperation < car.operationtime :
                        dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
                    car.Speed = 0
                    toperation = time()
                    while time()-toperation < car.operationtime :
                        dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
                    #testa o angulo de saída da parede
                    err, angles = sim.simxGetObjectOrientation(car.connectionID, car.pioneer, car.walls[i], sim.simx_opmode_buffer)
                    outangle = angles[2]*180/pi
                    print("outangle: ", outangle)
                    #se for menor que 10º, vira mais um pouco
                    if ((outangle <= 10 and outangle >= 0) or (outangle == 0)):
                        car.ddrive(0, 20, waux=-pi/2)
                        toperation = time()
                        while time()-toperation < car.operationtime :
                            dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
                        car.Speed = 0
                        toperation = time()
                        while time()-toperation < car.operationtime :
                            dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
                elif inangle > -90 and inangle <=0:
                    #para para entrar no modo curva
                    car.Speed = 0
                    toperation = time()
                    while time()-toperation < car.operationtime :
                        dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
                    #Turn 90º
                    car.ddrive(0, 90, waux=pi/2)
                    toperation = time()
                    while time()-toperation < car.operationtime :
                        dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
                    car.Speed = 0
                    toperation = time()
                    while time()-toperation < car.operationtime :
                        dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
                    #testa o angulo de saída da parede
                    _, angles = sim.simxGetObjectOrientation(car.connectionID, car.pioneer, car.walls[i], sim.simx_opmode_buffer)
                    outangle = angles[2]*180/pi
                    print("outangle: ", outangle)
                    #se for menor que 10º, vira mais um pouco
                    if outangle >= -10:
                        car.ddrive(0, 30, waux=pi/2)
                        toperation = time()
                        while time()-toperation < car.operationtime :
                            dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
                        car.Speed = 0
                        toperation = time()
                        while time()-toperation < car.operationtime :
                            dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
        dataCaller(f1, f2, count1, count2, tref, car,V, Aa, do0, finder, data)
        tloop0 = time()
        prev_detect = detect

def main():
    #connect to simulator
    conn = SimConnection()
    if conn.id == -1:
        sys.exit("Could not connect.")
    error_code, ping = sim.simxGetPingTime(conn.id)
    ping = ping/1000
    print("Running with ping of " + str(ping) + " s.")
    print("-------------------------------")
    
    #create objects 
    car = P3DX(connectionID=conn.id)
    finder = RSS(conn.id)
    
    #abre o arquivo e inicia um novo dataset

    data = open("data.txt", "a")
    data.write("\n New dataset\n")
    data.write("Velocidade | aceleração angular | Posição (RSS) | time | Posição real\n")
    
    #chamarautopilot
    autopilot(car, 0.2, data, finder)
    #escreva aqui o código

    #Encerra a conexão
    print("-------------------------------")
    print('closing connection')
    sleep(0.25) #tempo para garantir o envio do ultimo comando
    conn.close() #encerra a conexão com o simulador
    data.close()
    
    
#start
if __name__ == '__main__':
    main()