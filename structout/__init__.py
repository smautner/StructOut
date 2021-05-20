

from structout.graph import gprint
from structout.intlist import lprint, dprint, npprint


def bins(values,minmax=True,length=-1,method='bins',methodhow=16,**kwargs):
    npprint(values,minmax=minmax,length=length,method=method,methodhow=methodhow,**kwargs)
