# PyVISA is a Python package that enables you to control all kinds of
# measurement devices independently of the interface
# (e.g. GPIB, RS232, USB, Ethernet).
# (e.g. National Instruments, Agilent, Tektronix, Stanford Research Systems).

import visa
import struct
import matplotlib.pyplot as plt
import numpy as np
import skrf as rf



rm = visa.ResourceManager()

rm.list_resources()

inst = rm.open_resource('GPIB0::16::INSTR')
# inst = rm.open_resource('ASRL3::INSTR')



print(inst.query("*IDN?"))

# print(inst.query("OPC?;PRES;"))

n=float(inst.query("POIN?")) # read in default trace length

fs=float(inst.query("STAR?")) # read in the start f

fe=float(inst.query("STOP?")) # read in the stop f

# f=np.linspace(fs, fe, n)

# f=f/10**6  # unit MHz

f = rf.Frequency(fs/10**6,fe/10**6,n,'mhz')



inst.write('CHAN1')

inst.write('RFLP')  # selects REFLECTION
# inst.write('TRAP')  # selects TRANSMISSN

inst.write('LINM')
# inst.write('LOGM')
# inst.write('SWR')

inst.query("OPC?;SING")
# inst.query("OPC?;SWPSTART")

inst.write('MARK1;SEAMIN') # turn on marker 1, find the maximum

print(inst.query("OUTPMARK;")) # request the current marker value, read value



inst.write('FORM5')

inst.write('OUTPDATA;')

x=inst.read_raw()

y=x[4:]   # len(y)=1608

z=[y[i:i+4] for i in range(0, len(y), 4)]   # len(z)=402 , 4byte float

flts=[]

for flt in z :
    s=str(struct.unpack('f', flt))
    flts.append(float(s[1:-2]))

compx=[flts[i]+1j*flts[i+1] for i in range(0, len(flts), 2)]

c=np.array(compx)

DUT=rf.Network(frequency=f, s=c, z0=50)



rf.stylely()
fig=plt.figure(1)
plt.subplot(211)
plt.title('Reflection Log-Magnitude')
DUT.plot_s_db()
DUT.s11['100-1600mhz'].plot_s_db(lw=2,label='Band of Interest')
plt.subplot(212)
plt.title('Reflection Phase')
DUT.plot_s_deg()

plt.figure(2)
plt.title('Smith Chart')
DUT.plot_s_smith()

plt.figure(3)
plt.title('Complex Plane')
DUT.plot_s_complex()
plt.axis('equal')

plt.figure(4)
plt.title('Standing Wave Ratio')
DUT.plot_s_vswr()

plt.figure(5)
gd = abs(DUT.group_delay) *1e9 # in ns
plt.title('Group Delay')
plt.ylabel('Group Delay (ns)')
DUT.plot(gd)
