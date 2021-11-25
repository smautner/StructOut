

from structout.graph import gprint
from structout.intlist import dprint
from structout.intlistV2 import lprint, npprint, iprint


#def bins(values,minmax=True,length=-1,method='bins',methodhow=16,**kwargs):
#    npprint(values,minmax=minmax,length=length,method=method,methodhow=methodhow,**kwargs)



def hist(values):
    from collections import Counter
    counts = Counter(values)
    k=counts.keys()
    val  = [counts.get(i,0) for i in range(min(k), max(k)+1)]
    lprint(val)

