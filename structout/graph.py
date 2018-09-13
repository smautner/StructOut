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





def set_print_symbol(g, colorstyle='normal', nodelabel='label', edgelabel='label'):


    if type(colorstyle) == str:
        if colorstyle == "bw": # white

            for n, d in g.nodes(data=True):
               d['asciisymbol'] = d.get(nodelabel,str(n))

            if edgelabel != None:
                for a,b,d in g.edges(data=True):
                    if d.get(edgelabel,None):
                        d['asciisymbol'] = d[edgelabel]

        else: # default color

            for n, d in g.nodes(data=True):
               d['asciisymbol'] = color(d.get(nodelabel, str(n)), 'red')

            if edgelabel != None:
                for a,b,d in g.edges(data=True):
                    if d.get(edgelabel,None):
                        d['asciisymbol'] = color(d[edgelabel], 'blue')


    else: # colorlists
        for nodes, col in zip (colorstyle, ["magenta", "cyan", "yellow", "red", "blue", "green"]):
           for n in nodes:
               g.node[n]['asciisymbol'] = color(g.node[n].get(nodelabel,str(n)), col)
        for n,d in g.nodes(data=True):
            if "asciisymbol" not in d:
                g.node[n]['asciisymbol'] = color(g.node[n].get(nodelabel,str(n)), 'black')





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
                colorstyle='normal',
                pos=None):
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
                canvas[y][x] = "." if colorstyle=='bw' else color('.', 'black')[0]
                lastwritten_edge=(y,x)

        if lastwritten_edge and colorstyle != 'bw' and type(graph)==nx.DiGraph:
                canvas[lastwritten_edge[0]][lastwritten_edge[1]] = color('.', col='blue')[0]


    canvas = '\n'.join([''.join(e) for e in canvas])
    if debug:
        path = "%s/%s.dot" % (debug, hash(graph))
        canvas += "\nwriting graph:%s" % path
        nx.write_dot(graph, path)

    return canvas


######
# contract and horizontalize
######

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
                 color="normal",
                 nodelabel='label',
                 edgelabel='label',
                 size=10,
                 debug=None,
                 pos=None,
                 n_graphs_per_line= 5):

    if type(g) != list:
        g = [g]
        color = [color]
    else:
        # g is already a list
        if type(color) !=list:
            color = [color]*len(g)



    g = list(map(lambda x, col: set_print_symbol(x, colorstyle=col, nodelabel=nodelabel, edgelabel=edgelabel), g, color))
    g = map(lambda x,col: nx_to_ascii(x, size=size, debug=debug, colorstyle=col, pos=pos), g, color)
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
    graph = nx.path_graph(5)
    gprint(graph)
    graph[3][4]['label']='brot'
    graph.node[0]['label']='null'
    gprint(graph)
    gprint(graph, color=([1,2,3],[4,0]))
    ginfo(graph)

''' 
getting coordinates of molecules...  the molecule thing should be in the eden package afair
import molecule
chem=molecule.nx_to_rdkit(graph)
m.GetConformer().GetAtomPosition(0)
transform coordinates
'''