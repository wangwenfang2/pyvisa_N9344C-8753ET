# PyVISA is a Python package that enables you to control all kinds of
# measurement devices independently of the interface
# (e.g. GPIB, RS232, USB, Ethernet).
# (e.g. National Instruments, Agilent, Tektronix, Stanford Research Systems).

# N9344C , IP : 192.168.0.112 , gateway : 192.168.0.1 , submask : 255.255.255.0
# PC     , IP : 192.168.0.111 , gateway : 192.168.0.1 , submask : 255.255.255.0
# PC CMD : ping 192.168.0.112

import visa
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox


class instrument:
    def __init__(self, ax): 
        rm = visa.ResourceManager()
        rm.list_resources()
        # self.inst = rm.open_resource('TCPIP0::192.168.0.112::inst0::INSTR')
        self.inst = rm.open_resource('USB0::2391::65519::CN0604A475::0::INSTR')
        print(self.inst.query("*IDN?"))
        self.ax=ax
        self.startf=float(self.inst.query("SENS:FREQ:STAR?"))/float(1000000)
        self.stopf =float(self.inst.query("SENS:FREQ:STOP?"))/float(1000000)
        self.span =float(self.inst.query("SENS:FREQ:SPAN?"))/float(1000000)
        self.fs=np.arange(self.startf, self.stopf+self.span/460, self.span/460) #461
        self.ref_lev=float(self.inst.query("DISP:WIND:TRAC:Y:RLEV?"))
        self.line = Line2D(self.fs, np.zeros(461))
        self.ax.add_line(self.line)
        self.ax.set_xlim(self.startf, self.stopf)
        self.ax.set_ylim(int(self.ref_lev)-100, int(self.ref_lev))
    def inst_query(self):
        self.date=self.inst.query("SYSTem:Date?")
        self.centf=float(self.inst.query("SENS:FREQ:CENT?"))/float(1000000) #MHz
        self.startf=float(self.inst.query("SENS:FREQ:STAR?"))/float(1000000)
        self.stopf =float(self.inst.query("SENS:FREQ:STOP?"))/float(1000000)
        self.span =float(self.inst.query("SENS:FREQ:SPAN?"))/float(1000000)
        self.fs=np.arange(self.startf, self.stopf+self.span/460, self.span/460) #461
        self.swt=float(self.inst.query("SENS:SWE:TIME?"))   # second
        self.ref_lev=float(self.inst.query("DISP:WIND:TRAC:Y:RLEV?"))
        self.att=int(self.inst.query("SENS:POW:RF:ATT?"))
        self.RBW=float(self.inst.query("SENS:BAND:RES?"))/float(1000)  #KHz
        self.VBW=float(self.inst.query("SENS:BAND:VID?"))/float(1000)
        print('All queryed OK!')
    def inst_update(self, y):
        self.ax.set_xlim(self.startf, self.stopf)
        self.ax.set_ylim(int(self.ref_lev)-100, int(self.ref_lev))
        self.ax.figure.canvas.draw()
        self.line.set_data(self.fs, y)
        return self.line,


fig, ax = plt.subplots()

plt.subplots_adjust(bottom=0.25)

hsa=instrument(ax)

hsa.inst_query()



plt.title('N9344C Spectrum Analyzer')
plt.xlabel('Frequncy(MHz)')
plt.ylabel('Power (dBm)')
plt.grid(True)



def gen() :
    while True :
        x=np.array([])
        hsa.inst.write('TRACe:DATA? TRACe1')
        data=hsa.inst.read()
        strs=data.split(',')
        for s in strs :
            x=np.append(x, float(s))
        yield x

ani = animation.FuncAnimation(fig, hsa.inst_update, gen,
                              interval=int(hsa.swt*1000))

axcolor = 'lightgoldenrodyellow'
# ----- radio -----
rax = plt.axes([0.08, 0.03, 0.16, 0.16], facecolor=axcolor)
radio = RadioButtons(rax, ('ATT 0 dB', 'ATT 10 dB', 'ATT 20 dB'), active=0)

def attfunc(label):
    print(label)
    
radio.on_clicked(attfunc)
# -----------------
# ----- textbox1 -----
axbox1 = plt.axes([0.35, 0.15, 0.1, 0.04])
text_box1 = TextBox(axbox1, 'REF(dBm)', initial=str(hsa.ref_lev))

def submit(text):
    ydata = eval(text)
    print(ydata)

text_box1.on_submit(submit)
# -------------------
# ----- textbox2 -----
axbox2 = plt.axes([0.35, 0.09, 0.1, 0.04])
text_box2 = TextBox(axbox2, 'RBW(KHz)', initial=str(hsa.RBW))

text_box2.on_submit(submit)
# -------------------
# ----- textbox3 -----
axbox3 = plt.axes([0.35, 0.03, 0.1, 0.04])
text_box3 = TextBox(axbox3, 'VBW(KHz)', initial=str(hsa.VBW))

text_box3.on_submit(submit)
# -------------------
# ----- textbox4 -----
axbox4 = plt.axes([0.65, 0.15, 0.1, 0.04])
text_box4 = TextBox(axbox4, 'Center Frq(MHz)', initial=str(hsa.centf))

text_box4.on_submit(submit)
# -------------------
# ----- textbox5 -----
axbox5 = plt.axes([0.65, 0.09, 0.1, 0.04])
text_box5 = TextBox(axbox5, 'SPAN(MHz)', initial=str(hsa.span))

text_box5.on_submit(submit)
# -------------------
# ----- textbox6 -----
axbox6 = plt.axes([0.65, 0.03, 0.1, 0.04])
text_box6 = TextBox(axbox6, 'Sweep Time(s)', initial=str(hsa.swt))

text_box6.on_submit(submit)
# -------------------
# ----- button -----
exeax = plt.axes([0.77, 0.12, 0.12, 0.07])
button1 = Button(exeax, 'Execute', color=axcolor, hovercolor='0.975')
    
def exe(event):
    if not(text_box4.text==str(hsa.centf) and text_box5.text==str(hsa.span)) :
        print('Frequency Change!')
        hsa.startf=float(text_box4.text)-float(text_box5.text)/2
        hsa.stopf=float(text_box4.text)+float(text_box5.text)/2
        hsa.centf=float(text_box4.text)
        hsa.span=float(text_box5.text)
        hsa.fs=np.arange(hsa.startf, hsa.stopf+hsa.span/460, hsa.span/460)
    if not(text_box1.text==str(hsa.ref_lev)) :
        hsa.ref_lev=float(text_box1.text)
    hsa.inst.write('SENS:POW:RF:ATT 0')
    hsa.inst.write('DISP:WIND:TRAC:Y:RLEV '+text_box1.text)
    hsa.inst.write('SENS:BAND:RES '+text_box2.text+'e3')
    hsa.inst.write('SENS:BAND:VID '+text_box3.text+'e3')
    hsa.inst.write('SENS:FREQ:CENT '+text_box4.text+'e6')
    hsa.inst.write('SENS:FREQ:SPAN '+text_box5.text+'e6')
    
button1.on_clicked(exe)
# ------------------
# ----- button -----
resetax = plt.axes([0.77, 0.03, 0.12, 0.07])
button2 = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

def reset(event):
    radio.set_active(0)
    text_box1.set_val(str(-20))   # hsa.ref_lev
    text_box2.set_val(str(10))    # hsa.RBW
    text_box3.set_val(str(10))    # hsa.VBW
    text_box4.set_val(str(98))    # hsa.centf
    text_box5.set_val(str(20))    # hsa.span
    text_box6.set_val(str(0.039)) # hsa.swt

button2.on_clicked(reset)
# ------------------

plt.show()


    
