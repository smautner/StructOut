import math
import networkx as nx
from pprint import pprint
from networkx.algorithms.shortest_paths.unweighted import _single_shortest_path_length as short_paths


#########
# set labels and color them
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



def set_print_symbol(g, colorstyle='normal', nodelabel='label', edgelabel='label'):
    '''
    g.graph[xx] are settings for how the lines between nodes (or edge-labels) are drawn
    node/edege['asciisymbol']  is what is the label how it will be drawn
    '''
    g.graph['generic edge'] =  "." if colorstyle=='bw' else color('.', 'black')[0]
    g.graph['digraphend'] =  color('.', col='blue')[0]
    g.graph['colored'] = colorstyle!='bw'

    if isinstance(colorstyle,str):
        if colorstyle == "bw": # white

            for n, d in g.nodes(data=True):
               d['asciisymbol'] = str(d.get(nodelabel,n))

            if edgelabel != None:
                for a,b,d in g.edges(data=True):
                    if d.get(edgelabel,None):
                        d['asciisymbol'] = d[edgelabel]

        else: # default color

            for n, d in g.nodes(data=True):
               d['asciisymbol'] = color( str(d.get(nodelabel, n)), 'red')

            if edgelabel != None:
                for a,b,d in g.edges(data=True):
                    if d.get(edgelabel,None):
                        d['asciisymbol'] = color(d[edgelabel], 'blue')

    else: # colorlists
        for nodes, col in zip (colorstyle, ["magenta", "cyan", "yellow", "red", "blue", "green"]):
           for n in nodes:
               g.nodes[n]['asciisymbol'] = color(str(   g.nodes[n].get(nodelabel,n)), col)
        for n,d in g.nodes(data=True):
            if "asciisymbol" not in d:
                g.nodes[n]['asciisymbol'] = color(  str( g.nodes[n].get(nodelabel,n)), 'black')
    return g


####
# graph to ascii canvas
###


def transform_coordinates(pos,ymax,xmax):
    weird_maxx = max([x for (x, y) in pos.values()])
    weird_minx = min([x for (x, y) in pos.values()])
    weird_maxy = max([y for (x, y) in pos.values()])
    weird_miny = min([y for (x, y) in pos.values()])

    xfac = (float((weird_maxx - weird_minx)) / xmax )or 1
    yfac = (float((weird_maxy - weird_miny)) / ymax )or 1
    for key in pos.keys():
        wx, wy = pos[key]
        pos[key] = (int((wx - weird_minx) / xfac), int((wy - weird_miny) / yfac))
        #pos["debug_%d" % key] = [wx,xfac,weird_minx,weird_maxx, wy,yfac,weird_miny, weird_maxy]
    return pos


def nx_to_ascii(graph,
                size=10,
                debug=None,
                pos=None):
    '''
        debug would be a path to the folder where we write the dot file.
        in: nxgraph, (see set print symbol for special fields)
        out: a string
    '''


    # set up canvas
    ymax = size
    xmax = ymax * 2
    canvas = [list(' ' * (xmax + 1)) for i in range(ymax + 1)]

    # layout
    if not pos:
        #pos = nx.graphviz_layout(graph, prog='neato', args="-Gratio='2'")
        #pos=nx.drawing.nx_agraph.graphviz_layout(graph, prog='neato', args="-Gratio='2'")
        pos=nx.spring_layout(graph)

    pos= transform_coordinates(pos,ymax,xmax)


    # draw nodes
    def write_on_canvas(x,y,text, nooverwrite=False):
        for e in text:
            if nooverwrite and canvas[y][x] != ' ':
                break
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

        #edgelabel
        if d.get('asciisymbol',None) != None:
            write_on_canvas( (ax+bx)//2 , (ay+by)//2 ,d['asciisymbol'], nooverwrite=True)

        resolution = max(3, int(math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)))
        dx = float((bx - ax)) / resolution
        dy = float((by - ay)) / resolution
        lastwritten_edge = None
        for step in range(resolution):
            x = int(ax + dx * step)
            y = int(ay + dy * step)
            if canvas[y][x] == ' ':
                canvas[y][x] = graph.graph['generic edge'] #"." if colorstyle=='bw' else color('.', 'black')[0]
                lastwritten_edge=(y,x)

        if lastwritten_edge and graph.graph.get('colored',False) and type(graph)==nx.DiGraph:
                canvas[lastwritten_edge[0]][lastwritten_edge[1]] = graph.graph['digraphend']


    canvas = '\n'.join([''.join(e) for e in canvas])
    if debug:
        path = "%s/%s.dot" % (debug, hash(graph))
        canvas += "\nwriting graph:%s" % path
        nx.write_dot(graph, path)

    return canvas




#######
# main printers
#######

def make_picture(g,
                 color="normal",
                 nodelabel='label',
                 edgelabel='label',
                 size=10,
                 debug=None,
                 pos=None,
                 zoomlevel = 4,
                 zoomnodes = [],
                 n_graphs_per_line= 5):



    # everything musst be lists:
    if type(g) != list:
        g = [g]
        color = [color]
        zoomnodes= [zoomnodes]
    else:
        # g is already a list
        if type(color) !=list:
            color = [color]*len(g)
        if len(zoomnodes) == 0:
            zoomnodes= [[]]*len(g)
        else:
            print("zoomnodes not supported for multiple graphs")

        


    # ZOOM 
    g = list(map( lambda gr, no: do_zoom(gr,zoomlevel,no) ,g,zoomnodes))

    # set colors
    g = list(map(lambda x, col: set_print_symbol(x, colorstyle=col, nodelabel=nodelabel, edgelabel=edgelabel), g, color))

    # make picture
    g = map(lambda x: nx_to_ascii(x, size=size, debug=debug, pos=pos), g)

    # group pictures into rows
    return makerows(list(g), n_graphs_per_line=n_graphs_per_line)


def do_zoom(gr,zoomlevel, no):
    if not no:
        return gr 
    oklist = [a for (a, b) in short_paths(gr,no, zoomlevel)]
    return gr.subgraph(oklist)

#################################
#  down here is utility stuff
#################################

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

def gprint(g, **kwargs):
    print(make_picture(g, **kwargs))

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
    # simple graph without labels or anything
    graph = nx.path_graph(5)
    gprint(graph)

    # adding some labels
    graph[3][4]['label']='brot'
    graph.nodes[0]['label']='null'
    gprint(graph)

    # grouping nodes for coloring ..
    gprint(graph, color=([1,2,3],[4,0]))
    ginfo(graph)
    gprint([graph,graph,graph])

''' 
getting coordinates of molecules...  the molecule thing should be in the eden package afair
import molecule
chem=molecule.nx_to_rdkit(graph)
m.GetConformer().GetAtomPosition(0)
transform coordinates
'''
