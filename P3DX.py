from time import sleep, time
from simulator import sim
from simulator import SimConnection
import math
from math import pi
import keyboard
import random

class P3DX:
    def __init__(self, connectionID,
                r=0.195/2, l = 0.381):
        self.connectionID = connectionID
        self.r = r #raio das rodas
        self.l = l #largura entre rodas
        self.speed= 0 #linear velocity
        self.operationtime = 0 #tempo para realizar a operação requerida pelo operador.
        self.walls = [0,0,0,0]
        self. distances = [0,0,0,0]
        self.speed = 0

        #get handles
        error_code, self.reference = sim.simxGetObjectHandle(self.connectionID, "Reference", sim.simx_opmode_blocking)
        assert error_code == 0, 'could not find the reference anchor.'
        error_code, self.pioneer = sim.simxGetObjectHandle(self.connectionID, 'Pioneer_p3dx', sim.simx_opmode_blocking)
        assert error_code == 0, 'could not connect to robot.'
        error_code, self.leftMotor = sim.simxGetObjectHandle(self.connectionID, "Pioneer_p3dx_leftMotor", sim.simx_opmode_blocking)
        assert error_code == 0, 'could not connect to leftMotor.'
        error_code, self.rightMotor = sim.simxGetObjectHandle(self.connectionID, "Pioneer_p3dx_rightMotor", sim.simx_opmode_blocking)
        assert error_code == 0, 'could not connect to rightMotor.'

        error_code, self.walls[0] = sim.simxGetObjectHandle(self.connectionID, "WallN", sim.simx_opmode_blocking)
        error_code, self.walls[1] = sim.simxGetObjectHandle(self.connectionID, "WallS", sim.simx_opmode_blocking)
        error_code, self.walls[2] = sim.simxGetObjectHandle(self.connectionID, "WallL", sim.simx_opmode_blocking)
        error_code, self.walls[3] = sim.simxGetObjectHandle(self.connectionID, "WallO", sim.simx_opmode_blocking)
        
        #seta o carro em uma posição inicial e coloca a caster wheel em sentido favorável ao movimento.
        sim.simxSetObjectPosition(self.connectionID, self.pioneer, self.reference, (0,0,0.145), sim.simx_opmode_oneshot)
        sim.simxSetObjectOrientation(self.connectionID, self.pioneer, -1 , (0,0,0), sim.simx_opmode_oneshot)
       
        sleep(0.01)
        #define os parâmetros de telemetria inicial e inicia o modo streaming.
        returncode, position = sim.simxGetObjectPosition(self.connectionID,self.pioneer,self.reference, sim.simx_opmode_streaming)
        self.position = [position[0], position[1]]

        returnCode, orientation = sim.simxGetObjectOrientation(self.connectionID, self.pioneer,-1, sim.simx_opmode_streaming)
        self.orientation = orientation[2]*180/pi

        for i in range(0,4):
                err, self.distances[i] = sim.simxCheckDistance(self.connectionID, self.pioneer, self.walls[i], sim.simx_opmode_streaming)
                err, ori = sim.simxGetObjectOrientation(self.connectionID, self.pioneer, self.walls[i], sim.simx_opmode_streaming)

    def getPosition(self):
        returncode, position = sim.simxGetObjectPosition(self.connectionID,self.pioneer,self.reference, sim.simx_opmode_buffer)
        self.position = [position[0], position[1]]
        return self.position

    def getVelocity(self, returnnumber = 1):
        code, velocity, angular = sim.simxGetObjectVelocity(self.connectionID, self.pioneer, sim.simx_opmode_buffer)
        v0 = math.sqrt((velocity[0]**2) + (velocity[1]**2) + (velocity[2]**2))
        if returnnumber == 1:
            return v0
        elif returnnumber == 2:
            return velocity
        else:
            return [v0, velocity]

    def getOrientation(self):
        returnCode, orientation = sim.simxGetObjectOrientation(self.connectionID, self.pioneer,-1, sim.simx_opmode_buffer)
        self.orientation = orientation[2]*180/pi
        return self.orientation


    def ddrive(self, rotRadius, angle, waux = pi/2):
        '''
        angle = angulo entre a velocidade anterior e seguinte à rotação em graus.
        
        rotRadius = raio de rotação do carro em metros.
        rotRadius < 0: curva para a direita;
        rotRadius > 0: curva para a esquerda;
        rotRadius = 0: curva em torno de si, para este modo o carro deve estar parado a fim de evitar
                       estresse sobre os motores, portanto lembre-se de enviar o comando self.Speed = 0,
                       esperar um tempo coerente para a parada e então chamar esta função com waux em radianos por segundo.
        
        waux = velocidade para operações iniciadas parado em radianos por segundo.
        '''
        
        #Teste: O carro está em movimento?
        #se não, use Vaux para rotacionar em torno do ponto.
        if self.speed == 0 or rotRadius == 0:
            wc = waux
        else:
            wc = self.speed/rotRadius
        #Direção diferencial velocidade das rodas
        wl = ( wc * (rotRadius - self.l / 2) )/self.r
        wr = ( wc * (rotRadius + self.l / 2) )/self.r
        #tempo de curva para o angulo dado
        self.operationtime = abs(angle)/(abs(wc)*(180/pi))
        #atualiza os valores de velocidade das rodas
        sim.simxSetJointTargetVelocity(self.connectionID, self.leftMotor, wl, sim.simx_opmode_streaming)
        sim.simxSetJointTargetVelocity(self.connectionID, self.rightMotor,wr, sim.simx_opmode_streaming)
        return
        
    def autopilot(self, speed):
        prev_detect = [False, False, False, False]
        tstart = time()
        while (time()-tstart) < 1200:
            cte = 1
            
            detect = [False, False, False, False]
            #Lê a distância entre o carro e cada parede
            for i in range(0,4):
                err, self.distances[i] = sim.simxCheckDistance(self.connectionID, self.pioneer, self.walls[i], sim.simx_opmode_buffer)
            #detecta se precisa virar de alguma parede
            i = 0
            for dist in self.distances:
                if dist <= 0.65:
                    detect[i] = True
                elif dist <= 0.4:
                    self.ddrive(0, 180*cte)
                i = i + 1
                self.Speed = speed
            #testa se precisa virar
            for i in range(0,4):
                if (detect[i] == True and detect[i] != prev_detect[i]):
                    print("parede", self.walls[i], "encontrada")
                    err, angles = sim.simxGetObjectOrientation(self.connectionID, self.pioneer, self.walls[i], sim.simx_opmode_buffer)
                    inangle = angles[2]*180/pi
                    print("inangle: ", inangle)
                    if (inangle >=-180 and inangle <= -90):
                        #para para entrar no modo curva
                        self.Speed = 0
                        sleep(self.operationtime)
                        #Turn 90º
                        self.ddrive(0, 90, waux=-pi/2)
                        sleep(self.operationtime)
                        self.Speed = 0
                        sleep(self.operationtime)
                        #testa o angulo de saída da parede
                        err, angles = sim.simxGetObjectOrientation(self.connectionID, self.pioneer, self.walls[i], sim.simx_opmode_buffer)
                        outangle = angles[2]*180/pi
                        print("outangle: ", outangle)
                        #se for menor que 10º, vira mais um pouco
                        if ((outangle <= 10 and outangle >= 0) or (outangle == 0)):
                            self.ddrive(0, 20, waux=-pi/2)
                            sleep(self.operationtime)
                            self.Speed = 0
                            sleep(self.operationtime)
                    elif inangle > -90 and inangle <=0:
                        #para para entrar no modo curva
                        self.Speed = 0
                        sleep(self.operationtime)
                        #Turn 90º
                        self.ddrive(0, 90, waux=pi/2)
                        sleep(self.operationtime)
                        self.Speed = 0
                        sleep(self.operationtime)
                        #testa o angulo de saída da parede
                        err, angles = sim.simxGetObjectOrientation(self.connectionID, self.pioneer, self.walls[i], sim.simx_opmode_buffer)
                        outangle = angles[2]*180/pi
                        print("outangle: ", outangle)
                        #se for menor que 10º, vira mais um pouco
                        if outangle >= -10:
                            self.ddrive(0, 20, waux=pi/2)
                            sleep(self.operationtime)
                            self.Speed = 0
                            sleep(self.operationtime)
      
            prev_detect = detect
        print("Saindo do piloto automático")
        self.Speed = 0
        sleep(self.operationtime)

            

    @property
    def Speed(self):
        return self.speed

    @Speed.setter
    def Speed(self, speed):
        '''
        Pass the speed in m/s.
        this property converts the given speed 
        (upper limit of 1.2m/s) to rad/s on the wheel
        then send a command to the P3DX joint to turn at
        that speed.
        '''
        #setspeed
        time = speed - self.speed
        signal = 1
        if speed <0:
            signal = -1
            speed = abs(speed)
        if speed > 0.5:
            speed = 0.5
        elif speed <0.2:
            time =0.2
        self.speed = speed*signal
        w = self.speed/self.r
        #update speed
        sim.simxSetJointTargetVelocity(self.connectionID, self.leftMotor, w, sim.simx_opmode_streaming)
        sim.simxSetJointTargetVelocity(self.connectionID, self.rightMotor, w, sim.simx_opmode_streaming)
        #Tempo que leva para o carro chegar na velocidade desejada
        self.operationtime = time






        '''
        Alternative autopilot
        prevchecker = [False, False, False, False]
        while True:
            checker = [False, False, False, False]
            if keyboard.is_pressed("s"):
                print("autopilot Stopped")
                self.Speed = 0
                sleep(self.operationtime)
                break
            count = 0
            for i in range(0,4):
                err, self.distances[i] = sim.simxCheckDistance(self.connectionID, self.pioneer, self.walls[i], sim.simx_opmode_buffer)
            for dist in self.distances:
                if dist <= 1.05:
                    checker[i] = True
                    count += 1
            if count >= 2:
                angle = 135
            elif count == 1:
                angle = 90
            else:
                angle = 0
            if angle != 0:
                if prevchecker == checker:
                    angle = angle/2
                self.ddrive(self.l/2, angle)
                sleep(self.operationtime)
                self.Speed = 0
                sleep(0.5)
            self.Speed = speed
            sleep(0.3)
            prevchecker = checker
        '''