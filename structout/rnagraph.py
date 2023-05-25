from lmz import Map,Zip,Filter,Grouper,Range,Transpose,Flatten


import RNA
from collections import defaultdict
import networkx as nx
import structout as so









def normalRNA(struct):

    rna_object = RNA.get_xy_coordinates(struct)
    pos = {i: (rna_object.get(i).X, rna_object.get(i).Y)
               for i in range(len(struct))}
    return pos





def rnaprint(g, struct):
    rna_object = RNA.naview_xy_coordinates(struct)
    rna_object = RNA.simple_xy_coordinates(struct)

    pos = {i: (rna_object[i].X, rna_object[i].Y)
               for i in range(len(struct))}

    print(pos)
    # pos = normalRNA(struct) # this is the normal way
    so.gprint(g,pos=pos, size = 40)
    so.gprint(g,pos=pos, size = 40)




def newcoo(g):

    # greedily assign coordinates

    breakpoint()
    #


def sequence_dotbracket_to_graph(seq_info=None, seq_struct=None):
    """Given a sequence and the dotbracket sequence make a graph.
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





def doit(se,st):

    # 1. make a tree structure
    lifo  = []

    blocks = []
    mode = 0
    cblock= 0
    for i,c in enumerate(st):
        if c == f'(':
            if mode == 1:
                   blocks.append(cblock)
            mode =  0
            lifo.append(i)

        if c == ')':
            # switch mode...
            if mode == 0:
                mode = 1
                # if cblock: blocks.append(cblock)
                cblock = (lifo.pop(),i)
            elif mode == 1:
                cblock = (lifo.pop(),i)

        print(i,mode,c,cblock, blocks)
    blocks.append(cblock)
    print(blocks)

def doit2(seq,stu):
    pairs = []
    lifo =[]
    for i,e in enumerate(stu):
        if  e ==f'(':
                   lifo.append(i)
        elif e == f')':
            pairs.append((lifo.pop(),i))
    conn = dict(pairs)
    conn.update({a:b for b,a in pairs})
    first = 0
    last = len(stu)

    return getnode(first,last,stu,conn)

def getnode(start,end,stu,conn):
    left = start
    right  = end
    #......(....).....(...)...
    children = []
    while left < right:
        print(f"{left=}")
        print(f"{right=}")
        if stu[left] == f'.':
            left+=1
        if stu[left] == f'(':
            if f')' not in stu[conn[left]+1: right]:
                print(f"{ conn=}")
                right = conn[left]
                left +=1
            else:
                children+=getnode(left,conn[left],stu,conn)
                left = conn[left]+1
                print(f"{ left=}{conn[left]}")
    return (left,right, start,end, children)



# from pyparsing import Word, alphas, Regex, OneOrMore
# unpaired = Regex(f'.*')
# left = Regex(f'[(.]*')
# right = Regex(f'[).]*')
# hairpin  = left + unpaired + right
# ml = OneOrMore(stem)
# stem  = ml | hairpin
# seed =  unpaired | stem
# print(greet.parseString(stu))

from lark import Lark

def getconn(seq,stu):
    pairs = []
    lifo =[]
    for i,e in enumerate(stu):
        if  e ==f'(':
                   lifo.append(i)
        elif e == f')':
            pairs.append((lifo.pop(),i))
    conn = dict(pairs)
    conn.update({a:b for b,a in pairs})
    return conn

grammar = '''
start:  ( L start R ) *
L: /\(/
R: /\)/

%ignore ","
'''

def test():
    seq = 'GACUCGACCUAGCGAGUAUAAACAGGCUUUAGGCUAGGAGCGUGACCACUUCGGUGGUCGGUAGCA'
    stu = '((((,,,),,,(,,,))),,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'
    seq = 'AAAAAAAAGGGGGGGGGGUUUUUUUUUUAAAAAAAAAAAA'
    stu = ',,,,((((,,((,,,)),,((,,,)),,((,,)))))),,'
    conn = getconn(seq, stu)

    p = Lark(grammar)
    z = p.parse(stu)
    print(p.parse(stu).pretty())

    pos = 0,0
    g = sequence_dotbracket_to_graph(seq, stu)
    posdict = {}


    # rnaprint(g,stu)

    # we want a pos dict: {nodeid:(x,y)}

    treesplit = { f'R':f"URD",
                    f'U':f"LUR",
                    f'D':f"LDR" }

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
    close = dict("RD UR DL".split())
    rev = dict("RL UD".split())


    def getposdict(blob,d, pos, duty):
        '''
        blob is ( S ) ... so we can draw the brackets and the relevant company
            and check the ccardinality of S
        '''
        r = {}

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
            pos = newpos(pos,d)
            pos = newpos(pos,treesplit[d][0])
            for i in range(blob[0].start_pos+1,blob[2].start_pos):
                r [i] =  pos
                pos = newpos(pos,close[d])

        return r






    posdict = getposdict(z.children,f'R',pos, (0, len(stu)))


    # posdict = {k:(v[1],v[0]) for k,v in posdict.items()}

    pos = nx.drawing.spring_layout(g, pos =posdict ,fixed = posdict.keys())
    so.gprint(g, pos = pos, size = (60,15) )











    # g = sequence_dotbracket_to_graph(seq,stu)

    #doit2(seq,stu)



