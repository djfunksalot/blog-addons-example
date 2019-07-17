#!/usr/bin/env python3
# basic device scanning script loops over ch2 and ch1 
# backgate on ch2+, src on ch1+
# to determine Dirac or Inflection Point
import time
import hardware
import numpy as np
import redis
redisClient = redis.StrictRedis(host='localhost',
                                port=6379,
                                db=0)
#vars
#analog range 5: -150mv to 150mv
if __name__ == '__main__':
    hw=hardware.Hw()
    hw.start()
    hw.stop()
