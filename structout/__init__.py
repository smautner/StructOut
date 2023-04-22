

from structout.graph import gprint
from structout.intlist import dprint
from structout.intlistV2 import lprint, npprint, iprint, doALine, str_to
from structout.heatmap import heatmap
import numpy as np


#def bins(values,minmax=True,length=-1,method='bins',methodhow=16,**kwargs):
#    npprint(values,minmax=minmax,length=length,method=method,methodhow=methodhow,**kwargs)



def hist_CounterBased(values):
    from collections import Counter
    counts = Counter(values)
    k=counts.keys()
    val  = [counts.get(i,0) for i in range(min(k), max(k)+1)]
    lprint(val)

def hist(values, bins = 40):
    val = np.histogram(values,density=False, bins = bins)
    print(str_to(min(values)),end = '')
    print(doALine(val[0],showrange = False), end = '')
    print(str_to(max(values)))

def testhist():
    hist([1,2,3,4,5,6,10], 40)
