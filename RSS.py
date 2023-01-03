from simulator import SimConnection
from simulator import sim
from math import sqrt


class RSS:
    def __init__(self, connectionID):
        #vetores
        self.transmissor = [0,0,0] #vetor de handles
        self.D = [0,0,0] #vetor de distâncias para triangulação
        #constantes
        self.connectionID = connectionID
        self.pioneerheight = 0.1387
        self.P1 = [ 1.20000,  2.49000, 0.75000]
        self.P2 = [-2.49000, -2.00000, 0.75000]
        self.P3 = [ 2.00000, -2.49000, 0.75000]
        #handles
        error_code, self.pioneer = sim.simxGetObjectHandle(self.connectionID, "Pioneer_p3dx", sim.simx_opmode_blocking)
        error_code, self.transmissor[0] = sim.simxGetObjectHandle(self.connectionID, "Transmissor1", sim.simx_opmode_blocking)
        error_code, self.transmissor[1] = sim.simxGetObjectHandle(self.connectionID, "Transmissor2", sim.simx_opmode_blocking)
        error_code, self.transmissor[2] = sim.simxGetObjectHandle(self.connectionID, "Transmissor3", sim.simx_opmode_blocking)
        error_code, self.reference = sim.simxGetObjectHandle(self.connectionID, "Reference", sim.simx_opmode_blocking)
        #start getting data
        d = []
        for i in range(3):
            code, d = sim.simxGetObjectPosition(self.connectionID, self.pioneer, self.transmissor[i], sim.simx_opmode_streaming)
            self.D[i] = float(((d[0]**2) + (d[1]**2))**0.5)
        
    def readDistances(self):
        d = []
        for i in range(3):
            code, d = sim.simxGetObjectPosition(self.connectionID, self.pioneer, self.transmissor[i], sim.simx_opmode_buffer)
            self.D[i] = float(((d[0]**2) + (d[1]**2))**0.5)
    
    def triangulate(self):
        x1,y1,x2,y2 = self.getIntersections(self.P1[0],self.P1[1],self.D[0],self.P2[0],self.P2[1],self.D[1])
        x3,y3,x4,y4 = self.getIntersections(x0=self.P1[0],y0=self.P1[1],r0=self.D[0],x1=self.P3[0],y1=self.P3[1],r1=self.D[2])
        if ((x1 == x3) and (y1 == y3)):
            return [x1, y1]
        elif ((x1 == x4) and (y1 == y4)):
            return [x1, y1]
        elif ((x2 == x3) and (y2 == y3)):
            return [x2, y2]
        else:
            return [x2, y2]
    
    def getIntersections(self, x0, y0, r0, x1, y1, r1):
        # circle 1: (x0, y0), radius r0
        # circle 2: (x1, y1), radius r1

        d=sqrt((x1-x0)**2 + (y1-y0)**2)
    
        # non intersecting
        if d > r0 + r1 :
            return None
        # One circle within other
        if d < abs(r0-r1):
            return None
        # coincident circles
        if d == 0 and r0 == r1:
            return None
        else:
            a=(r0**2-r1**2+d**2)/(2*d)
            h=sqrt(r0**2-a**2)
            x2=x0+a*(x1-x0)/d   
            y2=y0+a*(y1-y0)/d   
            x3=x2+h*(y1-y0)/d     
            y3=y2-h*(x1-x0)/d 

            x4=x2-h*(y1-y0)/d
            y4=y2+h*(x1-x0)/d
            
            return (x3, y3, x4, y4)
        
    def ReadSensor(self):
        self.readDistances()
        return self.triangulate()