import math
import networkx as nx

#########
# set print symbol
#########

def color(symbol, col='red', colordict={'black': 0, 'red': 1,
             'green': 2,
             'yellow': 3,
             'blue': 4,
             'cyan': 6,
             'magenta': 5,
             'gray': 7}):
    '''http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python'''
    return ['\x1b[1;3%d;48m%s\x1b[0m' % (colordict[col], e) for e in symbol]


def defaultcolor(d, edge=False):
    '''colors that are useful for graphlearn'''

    if edge:
        return "blue"

    if 'core' in d:
        return 'cyan'
    elif 'interface' in d:
        return 'magenta'
    elif 'edge' in d: # this is if edge is a node attribute. .. happens when eden expands a graph
        return 'blue'
    else:
        return 'red'


def set_print_symbol(g, bw=False, label='label', colorlabel=None, edgelabel=None, edgecolorlabel=None):
    '''
    :param g:  networkx graph
    :param bw: draw in black/white
    :param label:  g.node[label] is used, if not found, node id
    :param colorlabel:  use this color, if none use defaultcolor function
    :return:
        networkx graph, nodes have 'asciisymbol' annotation
    '''

    def setcolor(symbol,d, label, colorlabel, edge=False):
        if bw:
            d['asciisymbol'] = symbol
        elif colorlabel:
            d['asciisymbol'] = color(symbol, d[colorlabel])
        else:
            d['asciisymbol'] = color(symbol, defaultcolor(d,edge=edge))

    for n, d in g.nodes(data=True):
       setcolor(str(d.get(label,n)),d,label, colorlabel)

    if edgelabel != None:
        for a,b,d in g.edges(data=True):
            if d.get(edgelabel,None):
                setcolor(d[edgelabel], d, edgelabel, edgecolorlabel, edge=True)




    return g


####
# coordinate setter
###


def transform_coordinates(pos,ymax,xmax):
    weird_maxx = max([x for (x, y) in pos.values()])
    weird_minx = min([x for (x, y) in pos.values()])
    weird_maxy = max([y for (x, y) in pos.values()])
    weird_miny = min([y for (x, y) in pos.values()])

    xfac = float((weird_maxx - weird_minx)) / xmax
    yfac = float((weird_maxy - weird_miny)) / ymax
    for key in pos.keys():
        wx, wy = pos[key]
        pos[key] = (int((wx - weird_minx) / xfac), int((wy - weird_miny) / yfac))
        #pos["debug_%d" % key] = [wx,xfac,weird_minx,weird_maxx, wy,yfac,weird_miny, weird_maxy]
    return pos


#####
# draw
####
def nx_to_ascii(graph,
                size=10,
                debug=None,
                bw=False,
                pos=None,
                edgecolorlabel='edgecolorlabel'):
    '''
        debug would be a path to the folder where we write the dot file.
        in: nxgraph
        out: a string
    '''


    # set up canvas
    ymax = size
    xmax = ymax * 2
    canvas = [list(' ' * (xmax + 1)) for i in range(ymax + 1)]

    # layout
    if not pos:
        #pos = nx.graphviz_layout(graph, prog='neato', args="-Gratio='2'")
        pos=nx.drawing.nx_agraph.graphviz_layout(graph, prog='neato', args="-Gratio='2'")
    pos= transform_coordinates(pos,ymax,xmax)


    # draw nodes
    def write_on_canvas(x,y,text):
        for e in text:
            canvas[y][x] = e
            if x < xmax:
                x += 1
            else:
                break

    for n, d in graph.nodes(data=True):
        x, y = pos[n]
        write_on_canvas(x,y,d['asciisymbol'])


    # draw edges
    for a, b,d in graph.edges(data=True):
        ax, ay = pos[a]
        bx, by = pos[b]
        resolution = max(3, int(math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)))
        dx = float((bx - ax)) / resolution
        dy = float((by - ay)) / resolution
        lastwritten_edge = None
        for step in range(resolution):
            x = int(ax + dx * step)
            y = int(ay + dy * step)
            if canvas[y][x] == ' ':
                canvas[y][x] = "." if bw else color('.', col=graph[a][b].get(edgecolorlabel,'black'))[0]
                lastwritten_edge=(y,x)
        if lastwritten_edge and not bw and type(graph)==nx.DiGraph:
                canvas[lastwritten_edge[0]][lastwritten_edge[1]] = color('.', col='blue')[0]

        #edgelabel
        if d.get('asciisymbol',None) != None:
            write_on_canvas( (ax+bx)//2 , (ay+by)//2 ,d['asciisymbol'])

    canvas = '\n'.join([''.join(e) for e in canvas])
    if debug:
        path = "%s/%s.dot" % (debug, hash(graph))
        canvas += "\nwriting graph:%s" % path
        nx.write_dot(graph, path)

    return canvas


######
# contract and horizontalize
######

def contract_graph(graph):
    '''convenience for graphlearn/eden'''
    import eden.graph as eg
    graph = eg._revert_edge_to_vertex_transform(graph)
    return graph


def transpose(things):
    return map(list, zip(*things))


def makerows(graph_canvazes, n_graphs_per_line=5):

    allrows = ''
    while graph_canvazes:
        current = graph_canvazes[:n_graphs_per_line]
        g = map(lambda x: x.split("\n"), current)
        g = zip(*g) #transpose(g)
        res = ''
        for row in g:
            res += "  ".join(row) + '\n'
        allrows+=res
        graph_canvazes = graph_canvazes[n_graphs_per_line:]

    return allrows

#######
# main printers
#######

def make_picture(g,
                 bw=False,
                 colorlabel=None,
                 contract=False,
                 label='label',
                 size=10,
                 debug=None,
                 pos=None,
                 edgecolorlabel=None,
                 n_graphs_per_line= 5,
                 edgelabel=None):
    '''

    :param g:  network x graph
    :param bw:  black/white bool
    :param colorlabel: node-dict key that contains the desired color
    :param contract:
    :param label:  node dict key containing the symbol to print, default is 'label', node-if if label is none
    :param size:  size on in y dimension
    :param debug:  where to dump debug files, off if none
    :return:
        a string
    '''
    if type(g) != list:
        g = [g]

    if contract:
        g = map(contract_graph, g)

    g = map(lambda x: set_print_symbol(x, bw=bw, label=label, colorlabel=colorlabel, edgecolorlabel=edgecolorlabel, edgelabel=edgelabel), g)
    g = map(lambda x: nx_to_ascii(x, size=size, debug=debug, bw=bw, pos=pos,edgecolorlabel=edgecolorlabel), g)
    return makerows(list(g), n_graphs_per_line=n_graphs_per_line)


def gprint(g, **kwargs):
    print (make_picture(g, **kwargs))

from pprint import pprint
def ginfo(g):

    for n,d in g.nodes(data=True):
        d.pop('asciisymbol',None)
        print (n,)
        pprint (d)
    for a,b,d in g.edges(data=True):
        d.pop('asciisymbol',None)
        print (a,b,)
        pprint (d)


# test
if __name__ == "__main__":
    graph = nx.path_graph(11)
    gprint(graph)
    graph[3][4]['label']='brot'
    gprint(graph, edgelabel='label')
    ginfo(graph)

''' 
getting coordinates of molecules...  the molecule thing should be in the eden package afair
import molecule
chem=molecule.nx_to_rdkit(graph)
m.GetConformer().GetAtomPosition(0)
transform coordinates
'''