#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from os import listdir
from matplotlib.backends.backend_pdf import PdfPages
design = ''
try:
  design=sys.argv[1]
except:
  print(design)
filenames = listdir('data/' + design)
#dd=pd.DataFrame(data={'ts':[], 'id':[], 'Vg1':[], 'Vg2':[], 'Vr':[], 'set':[], 'cycle':[]})
dd=pd.DataFrame(data={'ts':[], 'id':[], 'cycle':[], 'Vg':[], 'Vb':[], 'Vr':[], 'set':[]})
for filename in filenames:
  if filename.endswith('.csv'):
    d=pd.read_csv('data/'+design+'/'+filename,header=None)
    d.columns = ['ts', 'id', 'cycle', 'Vg', 'Vb', 'Vr']
    d['set'] = filename
    dd=pd.concat([dd,d])

c=(0.15/32768)
r=940000
#R2 is resistor
dd['Vii'] = (dd['Vr'] - 32768)*c
#R1 is device
dd['Vi'] = .15 - dd['Vii']
dd['I'] = (dd['Vii']/r)
dd['Ri'] = dd['Vi']/dd['I']
dd['iR'] = 1/dd['Ri']
dd['date']=(pd.to_datetime(dd['ts'],unit='s')) 
dd['hour'] = dd['date'] - min(dd['date'])

distinct_keys = dd['id'].unique()

for i, key in enumerate(distinct_keys):
    title = design + ' ' + str(key)
    df_subset = dd[dd.id==key]
    df_subset.plot(y='iR',x='Vg', title=title)
    plotname = str(key) + '.png'
    plt.savefig(plotname)
    #plt.show()
