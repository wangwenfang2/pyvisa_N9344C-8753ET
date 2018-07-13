# PyVISA is a Python package that enables you to control all kinds of
# measurement devices independently of the interface
# (e.g. GPIB, RS232, USB, Ethernet).
# (e.g. National Instruments, Agilent, Tektronix, Stanford Research Systems).

# N9344C , IP : 192.168.0.112 , gateway : 192.168.0.1 , submask : 255.255.255.0
# PC     , IP : 192.168.0.111 , gateway : 192.168.0.1 , submask : 255.255.255.0
# PC CMD      : ping 192.168.0.112

import visa
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation



rm = visa.ResourceManager()

rm.list_resources()

inst = rm.open_resource('TCPIP0::192.168.0.112::inst0::INSTR')


# inst.write('*IDN?'); print(inst.read())
print(inst.query("*IDN?"))

date=inst.query("SYSTem:Date?")



# ----- instrument side -----

print(inst.query('MMEM:CAT? "C:\"'))

# inst.write('MMEM:COPY "C:\ABC.CSV", "C:\SUB\ABC.CSV"');

# inst.write('MMEM:DATA? "C:\ABC.CSV"');
inst.write('MMEM:DATA? "C:\T_2.JPG"');    # instrument directory


print(inst.values_format.is_binary, inst.values_format.datatype,
      inst.values_format.separator)
print(inst.chunk_size)

x=inst.read_raw()

y=x[8:]
print(x[:8], x[8:16])   # x[:8] : ascii code , x[8:] : binary code


# ----- PC side -----

# f=open('C:\\test\ABC.CSV', 'wb')
f=open('C:\\test\T_2.JPG', 'wb')    # PC directory
f.write(y)
f.close()




    


    
    
