#threading test
import threading as th
from time import sleep, perf_counter

def printperf_counter():
    t0 = perf_counter()
    t = 0
    while True:
        print("time passed: ",perf_counter()-t0, "\n")
        t +=perf_counter() - t0
        print("total time: ", t)
        t0 = perf_counter()
        sleep(1-(perf_counter()%1))
        
        

def printpaft():
    t0 = perf_counter()
    while True:
        print("time passed: ",perf_counter()-t0)
        print("wait for: ", 0.5-(perf_counter()%0.5))
        sleep(0.5-(perf_counter()%0.5))
        t0 = perf_counter()

th1 = th.Thread(target = printperf_counter)
sleep(0.1)
th2 = th.Thread(target = printpaft)

#th1.start()
th2.start()