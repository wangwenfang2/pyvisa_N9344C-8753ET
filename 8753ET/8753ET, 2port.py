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



print(inst.query("*IDN?"))

# print(inst.query("OPC?;PRES;"))



def read_compx(is_reflect):
    n=float(inst.query("POIN?")) # read in default trace length

    fs=float(inst.query("STAR?")) # read in the start f

    fe=float(inst.query("STOP?")) # read in the stop f

    f = rf.Frequency(fs/10**6,fe/10**6,n,'mhz')

    if is_reflect==True :
        inst.write('RFLP')  # selects REFLECTION
    else :
        inst.write('TRAP')  # selects TRANSMISSN

    inst.query("OPC?;SING")

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

    return f, c



fr, rfl=read_compx(1)
ft, tra=read_compx(0)
DUT11=rf.Network(frequency=fr, s=rfl, z0=50)
DUT21=rf.Network(frequency=ft, s=tra, z0=50)


rf.stylely()
fig=plt.figure(1)
plt.subplot(211)
plt.title('Reflection Log-Magnitude')
DUT11.plot_s_db(label = 'S11')
DUT21.plot_s_db(label = 'S21')
plt.subplot(212)
plt.title('Reflection Phase')
DUT11.plot_s_deg(label = 'S11')
DUT21.plot_s_deg(label = 'S21')

plt.figure(2)
plt.title('Smith Chart')
DUT11.plot_s_smith(label = 'S11')
DUT21.plot_s_smith(label = 'S21')

plt.figure(3)
plt.title('Complex Plane')
DUT11.plot_s_complex(label = 'S11')
DUT21.plot_s_complex(label = 'S21')
plt.axis('equal')

plt.figure(4)
plt.title('Standing Wave Ratio')
DUT11.plot_s_vswr(label = 'S11')
DUT21.plot_s_vswr(label = 'S21')

