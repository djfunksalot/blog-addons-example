#!/usr/bin/env python3
# basic device scanning script loops over ch2 and ch1 
# backgate on ch2+, src on ch1+
# to determine Dirac or Inflection Point
import logging as _logging
import comedi as _comedi
import gpib
import time
import sys
from psychopy import parallel
from statistics import median
#vars
MAX_SAMPLES = 128
LOG = _logging.getLogger('comedi-insn')
LOG.addHandler(_logging.StreamHandler())
LOG.setLevel(_logging.ERROR)
comedidev = '/dev/comedi0'
channel = 1
subdevice = 0
arange = 5;
aref = 'diff';
#number of measurements to average over for a single returned value
num_scans = 10


global polarity
def enableP():
    global curchan
    curchan=1


#hardware interface
class fakeHw(object):
    def start(self):
        print("starting")
    def setV(self,chanbias,vbias):
        print("chanbias: " + str(chanbias)) 
    def stop(self):
        print("stopping")
    def measure(self,arange,aref,num_scans):
        return(0)
    def syncDio(self):
        return(0)

class Hw(object):
    def __init__(self):
        self.curchan = False
        self.negative = False
        self.pm2812 = False
        self.hp6633a = False
        self.debug  = False
        self.simulate  = False
    #initialize power supplies and parallel port
    def start(self):
        #print("initializing")
        self.pm2812 = gpib.find("pm2812")
        self.hp6633a = gpib.find("6633a")
        #select channel 1 and enable
        self.port = parallel.ParallelPort(address=0x0378)
        gpib.write(self.pm2812,"INST:NSEL 1")
        gpib.write(self.pm2812,"OUTP ON")
        gpib.write(self.pm2812,"VOLT 0")
        #select channel 2 and enable
        gpib.write(self.pm2812,"INST:NSEL 2")
        gpib.write(self.pm2812,"OUTP ON")
        gpib.write(self.pm2812,"VOLT 0")
        #select 6633a
        gpib.write(self.hp6633a,"CLR")
        gpib.write(self.hp6633a ,"VSET 0")
        gpib.write(self.hp6633a,"OUTP ON")
        self.enable = True
        self.syncDio()

    def stop(self):
        #print("shutting down")
        #select channel 1, set to 0V disable output
        gpib.write(self.pm2812,"INST:NSEL 1")
        gpib.write(self.pm2812,"VOLT 0")
        gpib.write(self.pm2812,"OUTP OFF")
        #select channel 1, set to 0V disable output
        gpib.write(self.pm2812,"INST:NSEL 2")
        gpib.write(self.pm2812,"VOLT 0")
        gpib.write(self.pm2812,"OUTP OFF")
        gpib.write(self.hp6633a ,"VSET 0")
        gpib.write(self.hp6633a,"OUTP OFF")
        #set all lp off
        self.enable = False 
        self.syncDio()


    def syncDio(self):
        devices={1:'0000',2:'0001',3:'0010',4:'0011',5:'0100',6:'0101',7:'0110',8:'0111',9:'1000',10:'1001',11:'1010',12:'1011',13:'1100',14:'1101',15:'1110',16:'1111'}
        try:
            device = devices[self.deviceid]
        except:
            device = '0000'
        if(self.enable):
            enable = '1'
        else:
            enable = '0'
        if(self.negative):
            polarity = '1'
        else:
            polarity = '0'
        data = '00' + polarity + enable + '0000'
        self.port.setData(int(data,2))
        return(bin(self.port.readData())[2:].zfill(8))



    def setV(self,c,v):
        i_meas = 0
        v_meas = 0
        if(c != self.curchan):
            self.curchan=c
            msg="INST:NSEL " + str(self.curchan)
            if(self.debug): 
                print(msg)
            else:
                gpib.write(self.pm2812,msg)
        msg = "VOLT " + str(v)
        if(self.debug): 
            print(msg)
        else:
            gpib.write(self.pm2812,msg)
            time.sleep(0.5)
            gpib.write(self.pm2812,"MEAS:VOLT?")
            time.sleep(0.1)
            v_meas=gpib.read(self.pm2812,100)
            v_meas = float(v_meas.rstrip())
            if(self.negative):
                v_meas = -v_meas
            gpib.write(self.pm2812,"MEAS:CURR?")
            i_meas=gpib.read(self.pm2812,100)
            i_meas = float(i_meas.rstrip())
        time.sleep(.5)
        return([v_meas,i_meas])



    def measure(self,arange,aref,num_scans):
        device = _comedi.comedi_open(comedidev)
        if not device:
             raise Exception('error opening Comedi device {}'.format(
                comedidev))
        setup_read_insn = SetupReadInsn(
            subdevice=subdevice, channel=channel,
            aref=aref, range=arange, n_scan=num_scans)

        insns = setup_insns(
            device, [setup_gtod_insn, setup_read_insn, setup_gtod_insn])
        ret = _comedi.comedi_do_insnlist(device, insns)
        if ret != insns.n_insns:
            raise Exception('error running instructions ({})'.format(ret))
            ret = _comedi.comedi_close(device)
            if ret != 0:
                raise Exception('error closing Comedi device')

        array = _comedi.insn_array.frompointer(insns.insns)
        t1 = get_time_of_day(array[0])
        t2 = get_time_of_day(array[2])
        data = _comedi.lsampl_array.frompointer(array[1].data)
        vals = []
        for i in range(array[1].n):
            vals.append(data[i])
        #sig=str((sum(vals) / float(len(vals))))
        sig=float(median(vals))
        free_insns(insns)
        ret = _comedi.comedi_close(device)
        return(sig)

        


            
    def hpsetI(self,i):
        gpib.write(self.hp6633a ,"ISET " + str(i))
        time.sleep(0.5)
        gpib.write(self.hp6633a,"VOUT?")
        time.sleep(0.1)
        v_meas=gpib.read(self.hp6633a,100)
        v_meas = float(v_meas.rstrip())
        gpib.write(self.hp6633a,"IOUT?")
        time.sleep(0.1)
        i_meas=gpib.read(self.hp6633a,100)
        i_meas = float(i_meas.rstrip())
        return(v_meas,i_meas)

    def hpsetV(self,v):
        gpib.write(self.hp6633a ,"VSET " + str(v))
        time.sleep(0.5)
        gpib.write(self.hp6633a,"VOUT?")
        time.sleep(0.1)
        v_meas=gpib.read(self.hp6633a,100)
        v_meas = float(v_meas.rstrip())
        gpib.write(self.hp6633a,"IOUT?")
        time.sleep(0.1)
        i_meas=gpib.read(self.hp6633a,100)
        i_meas = float(i_meas.rstrip())
        return(v_meas,i_meas)

def insn_str(insn):
    return ', '.join([
            'insn: {}'.format(insn.insn),
            'subdev: {}'.format(insn.subdev),
            'n: {}'.format(insn.n),
            'data: {!r}'.format(insn.data),
            'chanspec: {}'.format(insn.chanspec),
            ])

def setup_gtod_insn(device, insn):
    insn.insn = _comedi.INSN_GTOD
    insn.subdev = 0
    insn.n = 2
    data = _comedi.lsampl_array(2)
    data[0] = 0
    data[1] = 0
    data.thisown = False
    insn.data = data.cast()
    insn.chanspec = 0
    return insn

def get_time_of_day(insn):
    assert insn.insn == _comedi.INSN_GTOD, insn.insn
    data = _comedi.lsampl_array.frompointer(insn.data)
    seconds = data[0]
    microseconds = data[1]
    return seconds + microseconds/1e6

class SetupReadInsn (object):
    def __init__(self, subdevice, channel, range, aref, n_scan):
        self.subdevice = subdevice
        self.channel = channel
        self.range = range
        self.aref = getattr(_comedi, 'AREF_{}'.format(aref.upper()))
        self.n_scan = n_scan

    def __call__(self, device, insn):
        insn.insn = _comedi.INSN_READ
        insn.n = self.n_scan
        data = _comedi.lsampl_array(self.n_scan)
        data.thisown = False
        insn.data = data.cast()
        insn.subdev = self._get_subdevice(device)
        insn.chanspec = _comedi.cr_pack(self.channel, self.range, self.aref)
        return insn

    def _get_subdevice(self, device):
        if self.subdevice is None:
            return _comedi.comedi_find_subdevice_by_type(
                device, _comedi.COMEDI_SUBD_AI, 0);
        return self.subdevice

def setup_insns(device, insn_setup_functions):
    n = len(insn_setup_functions)
    insns = _comedi.comedi_insnlist_struct()
    insns.n_insns = n
    array = _comedi.insn_array(n)
    array.thisown = False
    for i,setup in enumerate(insn_setup_functions):
        array[i] = setup(device, array[i])
    insns.insns = array.cast()
    return insns

def free_insns(insns):
    array = _comedi.insn_array.frompointer(insns.insns)
    array.thisown = True
    for i in range(insns.n_insns):
        insn = array[i]
        data = _comedi.lsampl_array.frompointer(insn.data)
        data.thisown = True
