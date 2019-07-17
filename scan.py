#!/usr/bin/env python3
# basic device scanning script loops over ch2 and ch1 
# backgate on ch2+, src on ch1+
# to determine Dirac or Inflection Point
import time
import hardware
import numpy as np
import redis
redisClient = redis.StrictRedis(host='localhost',port=6379,db=0)
#vars
#
simulate = True
#analog range 5: -150mv to 150mv
arange = 5;
aref = 'diff'
num_scans = 10
vmin = 0.0
#vmax = 1.0
vmax = 3.0
stepsize =  .1
#stepsize = 5
vbias = 0.13
chansupply = 1
chanbias = 2
cycles = 2
#devices we'll scan
devrange = range(1)
def sweep(vmin,vmax,stepsize):
    vlist = []
    for vout in np.arange(vmin, vmax, stepsize):
        vlist.append(np.around(vout,2))
    for vout in np.arange(vmin, vmax, stepsize):
        vlist.append(np.around(vmax-vout,2))
    vlist.append(0)
    return(vlist)

#scan the chip from 0:-vmax:0:vmax:0
#epoch: time of meaasurement
#dev: chip device number
#cycle: scan number 
#Vbg: backgate voltage
#vbias: src-drain resistor voltage
#val: adc mesurement value
#VbgSet power supply reported voltage
#VbgMeas: power supply reported voltage
#IbgMeas: power supply reported current
#chipid: name of the chip being scanned
def scan(vrange,devrange,hw):
    for i in range(0,cycles * 2):
        if i % 2 == 0:
            hw.negative = True
        else:
            hw.negative = False
        for vgate in vrange:
            hw.syncDio()
            vresult=hw.hpsetV(vgate)
            time.sleep(1) 
            VbgMeas=vresult[0]
            IbgMeas=vresult[1]
            for d in devrange:
                #booger.chan(d)
                #hw.deviceid = d
                #hw.syncDio()
                val=hw.measure(arange,aref,num_scans)
                if(hw.negative):
                    VbgSet = - + vgate
                else:
                    VbgSet = vgate
                epoch=time.time()
                measurement={'epoch':epoch,'dev':d,'cycle':i,'VbgSet':VbgSet,'VbgMeas':VbgMeas,'IbgMeas':IbgMeas,'vbias':vbias,'val':val}
                print(str(epoch) + "," + str(d) + "," + str(i)  + "," + str(VbgSet)  + "," + str(vbias) + "," + str(val))
                #print(measurement)
                redisClient.zadd('np1',measurement,'p')
                #input(VbgSet)
    hw.stop()

if __name__ == '__main__':
    if(simulate):
      hw=hardware.fakeHw()
    else:
      hw=hardware.Hw()

    hw.sim = simulate;
    hw.start()
    hw.setV(chanbias,vbias)
    vrange = sweep(vmin,vmax,stepsize)
    scan(vrange,devrange,hw)
