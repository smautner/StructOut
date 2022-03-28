from scipy.sparse import csr_matrix as csr
import os
import numpy as np
import math

"""
    rewriting to have better code..
    does not have all the features of intlist yet i think...
"""
def doALine(values, log = False, chunkF = max,showrange=True, symbols =  '▁▂▃▄▅▆▇█', colors = '0467', ylim = False, characterlimit = 99999):
    '''
        ylim should be in htere in case we print many lines
    '''
    # how many digits can we use?
    values = np.array(values)
    pre, post, space  = determine_characterlimit(values, characterlimit, showrange=showrange)
    values = horizontalsquish(values, space, chunkF)

    if log:
        values = np.log2(values)

    # -> discretize so we have a low number of symbols
    values = binning(values, count = len(symbols)*len(colors), ylim=ylim)
    symbols = decorate(values, symbols, colors)
    return pre+''.join(symbols)+post


##########################
def determine_characterlimit(values, characterlimit, showrange=True):
    '''
    return:
        pre and post strings and how many characters we can actually use for output
    '''
    if showrange:
        pre = str_to(values.min())+"|"
        post = "|"+str_to(values.max())
    else:
        pre = ''
        post=''
    maxlength = getcolumns()-len(pre+post)
    characterlimit -= len(pre+post)
    space = min(maxlength, len(values))
    return pre, post, space

def str_to(n):
    #if isinstance(n,int):

    if type(n) == int:
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
    if type(col) == str:
        return '\x1b[1;3%s;48m%s\x1b[0m' % (col, chr)

    # 24 bit
    else:
        r,g,b = [ str(int(c*255)) for c in col]

        #print(r,b,g)

        return "\x1b[38;2;" + r + ";" + g + ";" + b + "m" + chr + '\x1b[0m'

    raise Exception("IMPOSSIBLE")

def lprint(values,**kwargs):
    print (doALine(values,**kwargs))

def npprint(thing,shareylim=True, **kwargs):
    thing = csr(thing)
    if shareylim:
        kwargs['ylim'] = thing.min(), thing.max()
    for i in range(thing.shape[0]):
        a  = thing.getrow(i).todense().getA1()
        lprint(a,**kwargs)

def heatmap(matrix,**kwargs):
    canvas = np.empty((matrix.shape[0], matrix.shape[1]*2))
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            canvas[row,column*2] = matrix[row,column]
            canvas[row,column*2+1] = matrix[row,column]
    symbols = "█"
    # colorlist is generated like this:
    #matplotlib.cm.get_cmap('viridis', 128).colors[:,:-1].tolist()
    colors = [[0.267004, 0.004874, 0.329415], [0.269944, 0.014625, 0.341379], [0.272594, 0.025563, 0.353093], [0.274952, 0.037752, 0.364543], [0.277018, 0.050344, 0.375715], [0.278791, 0.062145, 0.386592], [0.280267, 0.073417, 0.397163], [0.281446, 0.08432, 0.407414], [0.282327, 0.094955, 0.417331], [0.28291, 0.105393, 0.426902], [0.283197, 0.11568, 0.436115], [0.283187, 0.125848, 0.44496], [0.282884, 0.13592, 0.453427], [0.28229, 0.145912, 0.46151], [0.281412, 0.155834, 0.469201], [0.280255, 0.165693, 0.476498], [0.278826, 0.17549, 0.483397], [0.277134, 0.185228, 0.489898], [0.275191, 0.194905, 0.496005], [0.273006, 0.20452, 0.501721], [0.270595, 0.214069, 0.507052], [0.267968, 0.223549, 0.512008], [0.265145, 0.232956, 0.516599], [0.262138, 0.242286, 0.520837], [0.258965, 0.251537, 0.524736], [0.255645, 0.260703, 0.528312], [0.252194, 0.269783, 0.531579], [0.248629, 0.278775, 0.534556], [0.244972, 0.287675, 0.53726], [0.241237, 0.296485, 0.539709], [0.237441, 0.305202, 0.541921], [0.233603, 0.313828, 0.543914], [0.229739, 0.322361, 0.545706], [0.225863, 0.330805, 0.547314], [0.221989, 0.339161, 0.548752], [0.21813, 0.347432, 0.550038], [0.214298, 0.355619, 0.551184], [0.210503, 0.363727, 0.552206], [0.206756, 0.371758, 0.553117], [0.203063, 0.379716, 0.553925], [0.19943, 0.387607, 0.554642], [0.19586, 0.395433, 0.555276], [0.192357, 0.403199, 0.555836], [0.188923, 0.41091, 0.556326], [0.185556, 0.41857, 0.556753], [0.182256, 0.426184, 0.55712], [0.179019, 0.433756, 0.55743], [0.175841, 0.44129, 0.557685], [0.172719, 0.448791, 0.557885], [0.169646, 0.456262, 0.55803], [0.166617, 0.463708, 0.558119], [0.163625, 0.471133, 0.558148], [0.160665, 0.47854, 0.558115], [0.157729, 0.485932, 0.558013], [0.154815, 0.493313, 0.55784], [0.151918, 0.500685, 0.557587], [0.149039, 0.508051, 0.55725], [0.14618, 0.515413, 0.556823], [0.143343, 0.522773, 0.556295], [0.140536, 0.530132, 0.555659], [0.13777, 0.537492, 0.554906], [0.135066, 0.544853, 0.554029], [0.132444, 0.552216, 0.553018], [0.129933, 0.559582, 0.551864], [0.126453, 0.570633, 0.549841], [0.124395, 0.578002, 0.548287], [0.122606, 0.585371, 0.546557], [0.121148, 0.592739, 0.544641], [0.120092, 0.600104, 0.54253], [0.119512, 0.607464, 0.540218], [0.119483, 0.614817, 0.537692], [0.120081, 0.622161, 0.534946], [0.12138, 0.629492, 0.531973], [0.123444, 0.636809, 0.528763], [0.126326, 0.644107, 0.525311], [0.130067, 0.651384, 0.521608], [0.134692, 0.658636, 0.517649], [0.14021, 0.665859, 0.513427], [0.146616, 0.67305, 0.508936], [0.153894, 0.680203, 0.504172], [0.162016, 0.687316, 0.499129], [0.170948, 0.694384, 0.493803], [0.180653, 0.701402, 0.488189], [0.19109, 0.708366, 0.482284], [0.202219, 0.715272, 0.476084], [0.214, 0.722114, 0.469588], [0.226397, 0.728888, 0.462789], [0.239374, 0.735588, 0.455688], [0.252899, 0.742211, 0.448284], [0.266941, 0.748751, 0.440573], [0.281477, 0.755203, 0.432552], [0.296479, 0.761561, 0.424223], [0.311925, 0.767822, 0.415586], [0.327796, 0.77398, 0.40664], [0.344074, 0.780029, 0.397381], [0.360741, 0.785964, 0.387814], [0.377779, 0.791781, 0.377939], [0.395174, 0.797475, 0.367757], [0.412913, 0.803041, 0.357269], [0.430983, 0.808473, 0.346476], [0.449368, 0.813768, 0.335384], [0.468053, 0.818921, 0.323998], [0.487026, 0.823929, 0.312321], [0.506271, 0.828786, 0.300362], [0.525776, 0.833491, 0.288127], [0.545524, 0.838039, 0.275626], [0.565498, 0.84243, 0.262877], [0.585678, 0.846661, 0.249897], [0.606045, 0.850733, 0.236712], [0.626579, 0.854645, 0.223353], [0.647257, 0.8584, 0.209861], [0.668054, 0.861999, 0.196293], [0.688944, 0.865448, 0.182725], [0.709898, 0.868751, 0.169257], [0.730889, 0.871916, 0.156029], [0.751884, 0.874951, 0.143228], [0.772852, 0.877868, 0.131109], [0.79376, 0.880678, 0.120005], [0.814576, 0.883393, 0.110347], [0.83527, 0.886029, 0.102646], [0.85581, 0.888601, 0.097452], [0.876168, 0.891125, 0.09525], [0.89632, 0.893616, 0.096335], [0.916242, 0.896091, 0.100717], [0.935904, 0.89857, 0.108131], [0.9553, 0.901065, 0.118128], [0.974417, 0.90359, 0.130215], [0.993248, 0.906157, 0.143936]]


    npprint(canvas,shareylim=True,symbols = symbols, colors = colors,showrange=False,**kwargs)
    print()
    lprint(np.linspace(matrix.min(),matrix.max(),20), colors=colors,symbols=symbols)

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
    print("heatmap")
    z=np.random.rand(10,10)
    heatmap(z)






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



