import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns

global i

def csv_gen():
    global i
    df2=pd.read_csv('spectrum.csv', skiprows=9, index_col=0)
    # df2.describe(); df2.mean(); df2.max()
    for i in range(df2.shape[0]):
    #for i in range(1):
        yield df2.iloc[i,:]

def init():
    pass
    
def update(data):
    global temp, temp_sum
    temp=np.maximum(temp,data)
    temp_sum+=data
    line.set_ydata(data)
    maxh.set_ydata(temp)
    avg.set_ydata(temp_sum/(i+1))
    return line, maxh, avg

df=pd.read_csv('spectrum.csv', nrows=9, index_col=0, header=None)
fs=np.linspace(float(df.values[5]),float(df.values[6]),461) # object->float

sns.set()
fig, ax =plt.subplots()
global temp, temp_sum
temp=float(df.values[4])*np.ones(461)-100
temp_sum=np.zeros(461)
line, = ax.plot(fs, temp, 'k', linewidth=1)
maxh, = ax.plot(fs, temp, 'r', linewidth=1)
avg, = ax.plot(fs, temp, 'g', linewidth=1)
    
plt.title('N9344C Spectrum Analyzer')
plt.xlabel('Frequncy(MHz)')
plt.ylabel('Power (dBm)')
df.index.name=None
df.columns=['']
plt.text(1, 1, df,fontsize=7, ha='center', va='center', transform=ax.transAxes)

ax.set_ylim(float(df.values[4])-100, float(df.values[4]))

ani = animation.FuncAnimation(fig, update, csv_gen, init_func=init,
                              interval=int(float(df.values[7])*1000), repeat=False)

Writer = animation.writers['ffmpeg']
writer = Writer(fps=24, metadata=dict(artist='Matplotlib'))

ani.save('spectrum.mp4', writer=writer)
