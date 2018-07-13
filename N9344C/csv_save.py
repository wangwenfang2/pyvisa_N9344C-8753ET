# PyVISA is a Python package that enables you to control all kinds of
# measurement devices independently of the interface
# (e.g. GPIB, RS232, USB, Ethernet).
# (e.g. National Instruments, Agilent, Tektronix, Stanford Research Systems).

# N9344C , IP : 192.168.0.112 , gateway : 192.168.0.1 , submask : 255.255.255.0
# PC     , IP : 192.168.0.111 , gateway : 192.168.0.1 , submask : 255.255.255.0
# PC CMD : ping 192.168.0.112

import visa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.animation as animation
import seaborn as sns
import time
from datetime import datetime
import threading



rm = visa.ResourceManager()

rm.list_resources()
# ('TCPIP0::192.168.0.112::inst0::INSTR', 'USB0::2391::65519::CN0604A475::0::INSTR')

# inst = rm.open_resource('TCPIP0::192.168.0.112::inst0::INSTR')
inst = rm.open_resource('USB0::2391::65519::CN0604A475::0::INSTR')


# inst.write('*IDN?'); print(inst.read())
print(inst.query("*IDN?"))

date=inst.query("SYSTem:Date?")

centf=float(inst.query("SENS:FREQ:CENT?"))/float(1000000)   # MHz
# inst.write('SENS:FREQ:CENT 50e6')

startf=float(inst.query("SENS:FREQ:STAR?"))/float(1000000)   # MHz

stopf =float(inst.query("SENS:FREQ:STOP?"))/float(1000000)   # MHz

span =float(inst.query("SENS:FREQ:SPAN?"))/float(1000000)
# inst.write('SENS:FREQ:SPAN 2e6')

swt=float(inst.query("SENS:SWE:TIME?"))   # second

ref_lev=float(inst.query("DISP:WIND:TRAC:Y:RLEV?"))
# inst.write('DISP:WIND:TRAC:Y:RLEV 20')

att=int(inst.query("SENS:POW:RF:ATT?"))

RBW=float(inst.query("SENS:BAND:RES?"))/float(1000)  # KHz
# inst.write('SENS:BAND:RES 1e3')

VBW=float(inst.query("SENS:BAND:VID?"))/float(1000)  # KHz

f=np.arange(startf,stopf,span/460)       # len(f)==460
fs=np.append(f, stopf)

dfh=pd.Series({'Model':'N9344C', 'Date':date[:-1], 'Start Freq(MHz)':startf,
               'Stop Freq(MHz)':stopf, 'Sweep(sec)':swt, 'Ref(dBm)':ref_lev,
               'ATT(dB)':att, 'RBW(KHz)':RBW, 'VBW(KHz)':VBW})


# about Once every swt sec
i=0
def time_func(i):
    inst.write('TRACe:DATA? TRACe1')
    data=inst.read()
    strs=data.split(',')
    arr=np.array(strs, dtype='float')
    
    i+=1
    t=time.localtime()
    t="%d-%d-%d %d:%d:%d" %(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    df=pd.DataFrame(arr.reshape((1,461)), columns=fs, index=[t])
    if i==1 :
        dfh.to_csv('spectrum.csv', header=False, mode='w')
        df.to_csv('spectrum.csv', header=True, mode='a')
    elif i>=100 :
        return 0
    else :
        df.to_csv('spectrum.csv', header=False, mode='a')
    
    timer=threading.Timer(interval=round(swt+0.005, 2), function=time_func, args=[i]).start()


time_func(0)
