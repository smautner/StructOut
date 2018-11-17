
import math



#############
# TRANSFORM SINGLE NUMBER
#############
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


def colorize_symbol(symbol, col):
    '''http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python'''
    return '\x1b[1;3%d;48m%s\x1b[0m' % (col, symbol)



def decorate_number(num):
    '''
    :param num:  integer
    :return:
        string, that integer in COMPRESSED and colored
    '''
    num =int_to_log2chr(num)
    return colorize_symbol (str(num), colorscheme.get(num, 8))


##########################
##   COMPRESS RANGES OF NUMBERS
########################

def resize_number_array(values, desired_length,chunk_operation=max):
    length=len(values)
    size= float(length)/desired_length
    values = [  chunk_operation(values[ int(i*size): int(math.ceil((i+1)*size))   ] )  for i in range(desired_length)]
    return values


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




###################
# COMBINE RESIZER WITH SINGLE NUMBER TRANSFORMER
###################
def numberdict_to_str(ndict, dlength,chunk_operation=max):
    ret = map(decorate_number, resize_number_dict(ndict, desired_length=dlength,chunk_operation=chunk_operation))
    return ''.join(ret)

def numberlist_to_str(pdict, dlength,chunk_operation=max):
    ret = map(decorate_number, resize_number_array(pdict, desired_length=dlength,chunk_operation=chunk_operation))
    return ''.join(ret)


###########
#print stuff
###########
def dprint(posdict,length=80, chunk_operation=max):
    print (numberdict_to_str(posdict,length, chunk_operation=chunk_operation))

def lprint(posdict,length=80, chunk_operation=max):
    print (numberlist_to_str(posdict,length, chunk_operation=chunk_operation))

if __name__ == "__main__":
    lprint(range(1000))
    dprint({x:x for x in range(1000)})



