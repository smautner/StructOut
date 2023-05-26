from lmz import Map,Zip,Filter,Grouper,Range,Transpose,Flatten
from collections import defaultdict
import networkx as nx
import structout as so
import numpy as np




def getvienna_pos(struct):
    '''alternative method... '''
    import RNA
    rna_object = RNA.get_xy_coordinates(struct)
    pos = {i: (rna_object.get(i).X, rna_object.get(i).Y)
               for i in range(len(struct))}
    return pos


def _sequence_dotbracket_to_graph(seq_info=None, seq_struct=None):
    """
    Given a sequence and the dotbracket sequence make a graph. useful for testing.

    Parameters
    ----------
    seq_info string
        node labels eg a sequence string
    seq_struct  string
        dotbracket string
    Returns
    -------
        returns a nx.Graph
        secondary struct associated with seq_struct
    """
    graph = nx.Graph()
    lifo = defaultdict(list)
    open_brace_string={")":"(",
                "]":"[",
                ">":"<"}
    for i, (c, b) in enumerate(zip(seq_info, seq_struct)):
        graph.add_node(i, label=c, position=i)
        if i > 0:
            graph.add_edge(i, i - 1, label='-', type='backbone', len=1)
        if b in ['(','[','<']:
            lifo[b].append(i)
        if b in [')',']','>']:
            j = lifo[open_brace_string[b]].pop()
            graph.add_edge(i, j, label='=', type='basepair', len=1)
    return graph



########################
# setting up grammar and direction translations
#######################
grammar = '''
start:  ( L start R ) *
L: /\(/
R: /\)/

%ignore ","
'''

# if the current orientation is KEY, and we see a multiloop, first child goes to value[0], etc
treesplit = { f'R':f"URD",
                f'U':f"LUR",
                f'D':f"LDR" }
# if the current direction is key, direction of closing bracket is value
close = dict("RD UR DL".split())
# reverse direction
rev = dict("RL UD DU LR".split())

# move into direction
def newpos(pos, d):
    if d == f'R':
        return pos[0]+1, pos[1]
    if d == f'U':
        return pos[0], pos[1]-1
    if d == f'D':
        return pos[0], pos[1]+1
    if d == f'L':
        return pos[0]-1, pos[1]
    else:
        assert False


###################################
# make the possition dict...
####################################

def getposdict(blob,d, pos, duty):
    '''
    recursively the tree to get a posdict containing all nodes

    blob:  is ( S ) ... so we can draw the brackets and the relevant company
        and check the ccardinality of S
    '''
    r = {}

    ########################
    # draw terminals in    "...( S )..."; the grammar checks for brackets only,
    # but we just draw the unpaired nucleotides until then too...
    #########################
    # adjust start possition... to accomodate left and right duty
    # breakpoint()
    leftlen = blob[0].start_pos - duty[0]
    rightlen = duty[1] - blob[2].start_pos
    diff = min(leftlen - rightlen +1 ,0)  # i assume the +1 compensates for a leftlenrightlen offby one...
    for i in range(abs(diff)):
        pos = newpos(pos,d)

    # shit unpaired left
    for i in range(duty[0], blob[0].start_pos):
        pos = newpos(pos,d)
        r[i] = pos

    # shit bracket
    pos = newpos(pos,d)
    r[blob[0].start_pos] =  pos
    # shit closing bracked
    waybackpos = newpos(pos,close[d])
    r[blob[2].start_pos] =  waybackpos

    # shit unpaired left
    for i in range(blob[2].start_pos+1,duty[1]):
        waybackpos = newpos(waybackpos,rev[d])
        r[i] = waybackpos


    #############################
    # here we take care of all nesting structures: stem, multiloop
    ###########################
    children = Grouper(blob[1].children,3)
    targets = treesplit[d]
    if len(children) == 1:
        r.update(getposdict(children[0],d,pos,(blob[0].start_pos+1, blob[2].start_pos)))

    elif len(children) == 2:
        r.update(getposdict(children[0],targets[0],pos,(blob[0].start_pos+1, children[1][0].start_pos)))
        r.update(getposdict(children[1],d,pos,(children[1][0].start_pos, blob[2].start_pos)))

    elif len(children) == 3:
        r.update(getposdict(children[0],targets[0],pos ,(blob[0].start_pos+1, children[1][0].start_pos)))
        r.update(getposdict(children[1],d,pos,(children[1][0].start_pos+1, children[2][0].start_pos)))
        r.update(getposdict(children[2],targets[2], newpos(newpos(pos,d),targets[2]),
                                                        (children[2][0].start_pos, blob[2].start_pos)))
    else:
        ############
        # unpaired nodes in hairpin,
        # originally i wanted to place them with graphviz but that looks shitty
        ###############
        pos = newpos(pos,d)
        #pos = newpos(pos,targets[0])
        pos = newpos(pos,rev[close[d]])
        for i in range(blob[0].start_pos+1,blob[2].start_pos):
            r [i] =  pos
            pos = newpos(pos,close[d])

    return r


def RNAprint(g,structure = None, size = 1):
    ###
    # get structure annotation right:
    #########
    stu = g.graph.get(f'structure', structure)
    if stu == None:
        assert False, f'no structure in {structure=} {g.graph}'
    def nani(ch):
        if ch in f'([<':
            return f'('
        if ch in f')]>':
            return f')'
        return f','
    stu = f''.join(Map(nani, stu))

    ####
    # calculate a possition for every character in the strcuture
    ########
    from lark import Lark
    p = Lark(grammar)
    z = p.parse(stu)
    # print(p.parse(stu).pretty())
    posdict = getposdict(z.children,f'R',(0,0), (0, len(stu)))


    #####
    # undocumented nodes get filled by spring layout:
    ########
    pos = nx.drawing.spring_layout(g, pos =posdict ,fixed = posdict.keys())

    ##########
    # making sure the graph proportions are ok,  and draw
    #############
    a = np.array(list(pos.values()))
    xmin,ymin = a.min(axis = 0)
    xmax,ymax = a.max(axis = 0)
    xr = int(size*(xmax-xmin))
    yr = int(size*(ymax-ymin))

    so.gprint(g, pos = pos, size = (xr*4,yr*2) )





def test():
    seq = 'GACUCGACCUAGCGAGUAUAAACAGGCUUUAGGCUAGGAGCGUGACCACUUCGGUGGUCGGUAGCA'
    stu = '((((,,,),,,(,,,))),,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'
    seq = 'AAAAAAAAGGGGGGGGGGUUUUUUUUUUAAAAAAAAAAAA'
    stu = ',,,,((((,,((,,,)),,((,,,)),,((,,)))))),,'
    g = _sequence_dotbracket_to_graph(seq, stu)
    g.graph[f'structure'] = stu

    RNAprint(g)




