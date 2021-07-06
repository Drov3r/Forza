 #from vjoy import vj, setCar
import numpy as np
import time
import socket
import struct
import time
from collections import deque
import math
import control
import Network


def clamp(n, minn, maxn): return max(min(maxn, n), minn)


def sign(x): return x and (1, -1)[x < 0]

def act(actions):
    #control.noall()
    if actions[0]==1:
        control.goForward()
    if actions[0] == 0:
        control.noForward()
    if actions[1]==1:
        control.goLeft()
    if actions[1] == 0:
        control.noLeft()
    if actions[2]==1:
        control.goBrake()
    if actions[2] == 0:
        control.noBrake()
    if actions[3]==1:
        control.goRight()
    if actions[3] == 0:
        control.noLeft()

class roc(object):
    def __init__(self, span):
        self.span = span
        self.t = time.time()
        self.v = 0
        self.r = 0.0

    def calc(self, v):
        t = time.time()
        if (v != self.v and t != self.t):
            vdiff = v - self.v
            tdiff = t - self.t
            self.v = v
            self.t = t
            self.r = vdiff / tdiff
        elif (t > self.t + self.span):
            self.r = 0.0
        return self.r

    def calc2(self, v):
        t = time.time()
        if (v != self.v):
            vdiff = v - self.v
            self.v = v
            self.t = t
            self.r = vdiff
        elif (t > self.t + self.span):
            self.r = 0.0
        return self.r


class rollroc(object):
    def __init__(self, span):
        self.span = span
        self.q = deque([[time.time(), 0]])

    def calc2(self, v):
        t = time.time()
        qt = t - self.span

        # Clean Up the Que
        while len(self.q) > 0 and self.q[0][0] < qt:
            self.q.popleft()

        # Add new entry
        self.q.append([t, v])

        # ROC
        c = len(self.q)
        return (self.q[c-1][1] - self.q[0][1])/self.span

    def calc(self, v):
        t = time.time()
        qt = t - self.span

        # Add new entry
        self.q.append([t, v])

        # Clean Up the Que
        first = self.q[0][0]
        while first < qt:
            self.q.popleft()
            if(len(self.q) <= 1):
                break
            first = self.q[0][0]

        # Average
        c = len(self.q)
        if c > 0:
            s = 0
            for x in self.q:
                s += x[1]
            # print(">", s, c, (s / c), v, 2*(v - (s / c)) / self.span)
            return 2*(v - (s / c)) / self.span
        else:
            return 0


slowing = 0
turn = 0.0
accel = 0.0
brake = 0.0
running = 0
turning = 0
brakeroc = roc("Brake")
turnroc = rollroc(0.1)
network=Network.NeuralNet()
np_load_old = np.load
np.load = lambda *a, **k: np_load_old(*a, allow_pickle=True, **k)
train_data = np.load('training_datav2.npy')
np.load = np_load_old
training_inputs= []
training_outputs= []

for row in train_data:
    training_inputs.append(row[0])
    training_outputs.append(row[1])






network.fit(np.array(training_inputs),np.array(training_outputs))


network.plot_loss()
print("trained")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 1614))
#vj.open()

MAX_MPS = 35

while True:
    data, addr = sock.recvfrom(4096)
    values = struct.unpack('<i I 27f 4i 20f 5i 12x 17f H 6B 3b x', data)
    t = time.time()
    #print("Slow:", round(values[84] / 1.27, 1), "Brake:", round(brake * 100, 1), "Accel:",
    #      round(accel * 100, 1), "Turn:", round(turn * 100, 1))
    if (values[0] > 0):
        if (not running):
            running = 1
        # STEER
        distance = values[83]
        #print("Line", values[83])
        rate = -turnroc.calc(distance)
        targettime = 1  # 1 + clamp(values[61] / 20, 0, 5)
        targetrate = distance / targettime
        turn = clamp((targetrate-rate)/256, -1, 1)
        # turn = sign(targetrate-rate) * math.pow(targetrate-rate, 2) / 1000
        # print(distance, targetrate,  round(rate, 2),  round(turn*100, 1))

        # SPEED
        # brakebase = (values[84] / 128.0)
        # brakerate = brakerate.calc(values[84])
        if (values[84] > 0):
            slowing = time.time()
            accel = 0
            brake = 1  # values[84]/64
        elif (t < slowing + 1):
            accel = 0
            brake = 0
        else:
             # 1-abs(turnbase+turnrate)
            # clamp(1 - (values[61] / 100), 0.2, 1)
            accel = 1 - clamp(abs(turn)-.25, 0, 0.5) - \
                clamp((values[61]-MAX_MPS)/10, 0, 1)
            brake = 0
        accel = 1
        #print("Slow:", round(values[84]/1.27, 1), "Brake:", round(brake*100, 1), "Accel:",round(accel*100, 1), "Turn:", round(turn*100, 1))

        #setCar(clamp(turn, -1, 1), accel, brake)
        speed=round(values[61])
        print([speed,values[84],accel,brake,turn])
        out1 =network.predict(np.array([speed,values[84],accel,brake,turn]))
        out=out1[0]
        # out[0]=round(out[0])
        # out[1]=round(out[1])
        # out[2]=round(out[2])
        # out[3]=round(out[3])
        print(out1)

        act(out)

    else:
        if (running):
            running = 0
            #setCar(0, 0, 0)

#vj.close()
