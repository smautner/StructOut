from scipy.sparse import csr_matrix as csr
import os
import numpy as np
import math



'''
taking care of int lists:

    1. compress 
    2. log/bin/whatwver
    3. color+numto symbol
    4. add min/max

then there is the numpy mode :) 
'''

##########################
##   COMPRESS -> horizontal
########################

def resize_number_array(values, desired_length,chunk_operation=max):
    length=len(values)
    size= float(length)/desired_length
    values = [  chunk_operation(values[ int(i*size): int(math.ceil((i+1)*size))   ] )  for i in range(desired_length)]
    return values

#################3
# COMPRESS -> fit the value in a neat integer
###############

def digitize(values, method = 'log', methodarg = 2): 
    if method == 'log':
         return [ int(math.log(i,methodarg)) for i in values]
    if method == 'bins':
        return bins(values,methodarg)



def bins(values,count):
        mi=min(values)
        ma=max(values)
        bins = np.arange(mi,ma+.0001,(ma-mi)/(count))
        bins[-1]+=.0001
        #print(bins)
        return np.digitize(values,bins)-1

    
###################
# int to chr 
####################


def decorate(values): 
    # there are 8 colors, so we distribute them over the space of used chars
    colors = bins(values,8)
    return map(colorize_number,values,colors)

def colorize_number(number, col):
    '''http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python'''
    number = int(number)
    number = str(number) if number < 10 else chr(number+55)
    return '\x1b[1;3%d;48m%s\x1b[0m' % (col, number)



############3
# letzgo 
###########

def str_to(n):

    if -10 < n < 10: 
        if isinstance(n,int):
            return str(n)
        return f"{n:.1}"
    else:
        return str(int(n))

def doALine(values,
        length=-1,minmax=False, chunk_operation=max, 
        method = 'log', methodhow =2):
    if length < 0:
        length = os.get_terminal_size().columns

    if minmax:
        pre = str_to(min(values))+"|"
        post = "|"+str_to(max(values))
    else:
        pre,post = '',''

    space = min(len(values), length-len(pre+post))
    values = resize_number_array(values,space,chunk_operation)
    values = digitize(values,method,methodhow)
    values = decorate(values)

    return pre+''.join(values)+post


def lprint(values,**kwargs):
    print (doALine(values,**kwargs))


def npprint(thing, **kwargs):
    thing = csr(thing) 
    for row in thing:
        intlist = row.todense().tolist()[0]
        lprint(intlist,**kwargs)


if __name__ == "__main__":
    lprint(range(1000), method = 'bins', methodhow=16)
    lprint(range(1000), method ='log', methodhow=2)
    z=np.random.rand(3,300)
    npprint(z,minmax=True, method='bins',methodhow=16)












#############
# legacy stuff for dictionaries... 
# i am rewriring this now  and this is not a current usecase
# the solution should be to use csr_sparse in the future
#############
def dprint(posdict,length=80, chunk_operation=max):
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
    ret = map(decorate_number, resize_number_dict(ndict, desired_length=dlength,chunk_operation=chunk_operation))
    return ''.join(ret)


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



