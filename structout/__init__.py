

from structout.graph import gprint
from structout.intlist import dprint
from structout.intlistV2 import lprint, npprint, iprint, doALine, str_to, scatter, plot, plot_braille, colorize
from structout.heatmap import heatmap
from structout.rnagraph import RNAprint
import numpy as np


#def bins(values,minmax=True,length=-1,method='bins',methodhow=16,**kwargs):
#    npprint(values,minmax=minmax,length=length,method=method,methodhow=methodhow,**kwargs)



def hist_CounterBased(values):
    from collections import Counter
    counts = Counter(values)
    k=counts.keys()
    val  = [counts.get(i,0) for i in range(min(k), max(k)+1)]
    lprint(val)

def hist_(values, bins = 40, xlim=None):
    val = np.histogram(values,density=False, bins = bins, range = xlim)
    print(str_to(min(values) if not xlim else xlim[0]),end = '|')
    print(doALine(val[0],showrange = False), end = '|')
    print(str_to(max(values) if not xlim else xlim[1]))


def hist(values, bins = 40, xlim=None, color = '1'):
    val,_ = np.histogram(values,density=False, bins = bins, range = xlim)
    print(str_to(min(values) if not xlim else xlim[0]),end = '|')
    text = plot_braille(np.arange(bins),val,rows = 1,cols=bins//2,xlim=np.array((0,bins)))[0]
    if color:
        text = colorize(text,'1')
    print(text, end = '|')
    print(str_to(max(values) if not xlim else xlim[1]))


def testhist():
    hist([1,2,3,4,5,6,10], 40)
