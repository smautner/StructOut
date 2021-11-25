from scipy.sparse import csr_matrix as csr
import os
import numpy as np
import math

"""
    rewriting to have better code..
    does not have all the features of intlist yet i think...
"""
def doALine(values, log = False, chunkF = max, symbols =  '▁▂▃▄▅▆▇█', colors = '0467', ylim = False, characterlimit = 99999):
    '''
        ylim should be in htere in case we print many lines
    '''
    # how many digits can we use?
    values = np.array(values)
    pre, post, space  = determine_characterlimit(values, characterlimit)
    values = horizontalsquish(values, space, chunkF)

    if log:
        values = np.log2(values)

    # -> discretize so we have a low number of symbols
    values = binning(values, count = len(symbols)*len(colors), ylim=ylim)
    symbols = decorate(values, symbols, colors)
    return pre+''.join(symbols)+post


##########################
def determine_characterlimit(values, characterlimit):
    '''
    return:
        pre and post strings and how many characters we can actually use for output
    '''
    pre = str_to(values.min())+"|"
    post = "|"+str_to(values.max())

    maxlength = getcolumns()-len(pre+post)
    characterlimit -= len(pre+post)
    space = min(maxlength, len(values))
    return pre, post, space

def str_to(n):
    #if isinstance(n,int):
    if 'int' in str(type(n)):
        return str(n)
    if -10 < n < 10:
        return f"{n:.3f}"
    if -100 < n < 100:
        return f"{n:.2f}"
    if -1000 < n < 1000:
        return f"{n:.1f}"
    else:
        return f"{n:.0f}"


def getcolumns():
    try:
        return os.get_terminal_size().columns
    except:
        return 100


##########################
def horizontalsquish(values, desired_length,chunk_operation=max):
    length=len(values)
    if length <=desired_length:
        return values
    size= float(length)/desired_length
    values = [  chunk_operation(values[ int(i*size): int(math.ceil((i+1)*size))   ] )  for i in range(desired_length)]
    return np.array(values)

def binning(values,count, ylim):
        #mi, ma = ylim if isinstance(ylim, tuple) else  (values.min(), values.max())
        mi, ma = ylim or  (values.min(), values.max())
        bins = np.arange(mi,ma+.0001,((ma+.0001)-mi)/(count))
        bins[-1]+=.0001
        return np.digitize(values,bins)-1



def decorate(values, symbols, colors):
    allcolors = [colorize(s,c) for s in symbols for c in colors]
    return ''.join([allcolors[i] for i in values])

def colorize(chr, col):
    '''
       http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
       https://pypi.org/project/colorama/
    '''
    #number = str(number) if number < 10 else chr(number+55)
    return '\x1b[1;3%s;48m%s\x1b[0m' % (col, chr)


def lprint(values,**kwargs):
    print (doALine(values,**kwargs))

def npprint(thing,shareylim=True, **kwargs):
    thing = csr(thing)
    if shareylim:
        kwargs['ylim'] = thing.min(), thing.max()
    for i in range(thing.shape[0]):
        a  = thing.getrow(i).todense().getA1()
        lprint(a,**kwargs)

def iprint(dic:dict,bins = 1000,spacemin=False, spacemax=False,  **kwargs): # indiscrete print
    keys = np.array(list(dic.keys()))
    spacemin =  spacemin or min(keys)
    spacemax =  spacemax or max(keys)
    discrete = np.digitize(keys, bins=np.linspace(spacemin, spacemax, bins ) )

    base = [min(dic.values())]*(bins+1)
    for k,e in zip(keys,discrete):
        base[e]=dic[k]

    lprint(base, **kwargs)

if __name__ == "__main__":
    lprint(range(1000))
    lprint(range(1000),  log = True)
    z=np.random.rand(2,300)
    npprint(z)
    z*=100
    npprint(z.astype(np.int64))
    npprint(z.astype(np.int64), log=True)
    d={0:3, 0.3:6,4:3, 21.4:0.2}
    iprint(d)






#############
# legacy stuff for dictionaries...
# i am rewriring this now  and this is not a current usecase
# the solution should be to use csr_sparse in the future
#############
def dprint(posdict,length=100, chunk_operation=max):
    print (numberdict_to_str(posdict,length, chunk_operation=chunk_operation))

def access_region(d,start,end):
    return [ v for pos,v in d.items() if start<=pos<=end  ]

def resize_number_dict(posdict, desired_length,chunk_operation=max):
    '''
    :param posdict:  {pos:NUMBER, etc}
    :param desired_length:
    :return:
    '''
    minn =min(posdict)
    maxx =max(posdict)
    length= maxx-minn
    size= float(length)/desired_length
    posdict = [chunk_operation([0]+access_region(posdict, int(i*size)+minn, int(math.ceil(i+1)*size+minn))) for i in range(desired_length)]
    return posdict


def numberdict_to_str(ndict, dlength,chunk_operation=max):
    ret =  resize_number_dict(ndict, desired_length=dlength,chunk_operation=chunk_operation)
    return "".join((decorate(ret)))







########3
# old coloring stuff
#########
colorscheme={
        0:0,
        1:0,
        2:4,
        3:4,
        4:1,
        5:1,
        6:3,
        7:3,
        '.':0
        }
def int_to_log2chr(i):
    '''
    :param i:  INTEGER
    :return:
        0 -> .
        1-9 -> 1-9
        10+  -> A+
    '''
    if i < 1:
        return '.'
    else:
        z= int(math.log(i,2))
        return z if z <=9 else chr(z+55)

def decorate_number(num):
    '''
    :param num:  integer
    :return:
        string, that integer in COMPRESSED and colored
    '''
    num =int_to_log2chr(num)
    return colorize_symbol (str(num), colorscheme.get(num, 8))



