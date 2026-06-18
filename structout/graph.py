from __future__ import annotations

import math
from typing import Any, Sequence
import networkx as nx
from pprint import pprint
from networkx.algorithms.shortest_paths.unweighted import _single_shortest_path_length as short_paths

COLORDICT: dict[str, int] = {
    'black': 0, 'red': 1, 'green': 2, 'yellow': 3,
    'blue': 4, 'cyan': 6, 'magenta': 5, 'gray': 7,
}


def color(symbol: Sequence[str], col: str = 'red', colordict: dict[str, int] | None = None) -> list[str]:
    """Wrap each string in ANSI color escape codes.

    Args:
        symbol: Strings to colorize.
        col: Color name (key in colordict).
        colordict: Custom color-name-to-index mapping.

    Returns:
        List of ANSI-escaped strings.
    """
    if colordict is None:
        colordict = COLORDICT
    return ['\x1b[1;3%d;48m%s\x1b[0m' % (colordict[col], e) for e in symbol]



def set_print_symbol(
    g: nx.Graph,
    colorstyle: str | list[Sequence[str]] = 'normal',
    nodelabel: str = 'label',
    edgelabel: str = 'label',
) -> nx.Graph:
    """Assign ASCII display symbols to nodes and edges based on color style.

    Args:
        g: NetworkX graph to annotate with display symbols.
        colorstyle: Color scheme; 'normal', 'bw', or list of node groups.
        nodelabel: Node attribute key to use as display label.
        edgelabel: Edge attribute key to use as display label.

    Returns:
        The same graph with ``asciisymbol`` attributes set on nodes/edges.
    """
    g.graph['generic edge'] =  "." if colorstyle=='bw' else color('.', 'gray')[0]
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


def transform_coordinates(
    pos: dict[Any, tuple[float, float]],
    ymax: int,
    xmax: int,
) -> dict[Any, tuple[int, int]]:
    """Normalize node positions to fit within a given canvas size.

    Args:
        pos: Mapping of node to ``(x, y)`` float coordinates.
        ymax: Maximum y dimension of the target canvas.
        xmax: Maximum x dimension of the target canvas.

    Returns:
        The same ``pos`` dict with coordinates scaled to integer grid positions.
    """
    weird_maxx = max([x for (x, y) in pos.values()])
    weird_minx = min([x for (x, y) in pos.values()])
    weird_maxy = max([y for (x, y) in pos.values()])
    weird_miny = min([y for (x, y) in pos.values()])

    xfac = (float((weird_maxx - weird_minx)) / xmax )or 1
    yfac = (float((weird_maxy - weird_miny)) / ymax )or 1
    for key in pos.keys():
        wx, wy = pos[key]
        pos[key] = (int((wx - weird_minx) / xfac), int((wy - weird_miny) / yfac))
    return pos


def nx_to_ascii(
    graph: nx.Graph,
    size: int | tuple[int, int] = 10,
    debug: str | None = None,
    pos: dict[Any, tuple[float, float]] | None = None,
) -> str:
    """Render a NetworkX graph as an ASCII string.

    Args:
        graph: NetworkX graph with ``asciisymbol`` attributes on nodes/edges.
        size: Canvas height, or ``(width, height)`` tuple.
        debug: If set, write a ``.dot`` file to this directory.
        pos: Pre-computed node positions; uses spring layout when ``None``.

    Returns:
        Multi-line string representing the graph in ASCII art.
    """


    # set up canvas
    if isinstance(size,int):
        ymax = size
        xmax = ymax * 2
    else:
        xmax,ymax = size
    canvas = [list(' ' * (xmax + 1)) for i in range(ymax + 1)]

    # layout
    if not pos:
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

        if lastwritten_edge and graph.graph.get('colored', False) and isinstance(graph, nx.DiGraph):
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

def make_picture(
    g: nx.Graph | list[nx.Graph],
    color: str | list[str] = "normal",
    nodelabel: str = 'label',
    edgelabel: str = 'label',
    size: int | tuple[int, int] = 10,
    debug: str | None = None,
    pos: dict[Any, tuple[float, float]] | None = None,
    zoomlevel: int = 4,
    zoomnodes: list[Any] = [],
    n_graphs_per_line: int = 5,
) -> str:
    """Produce a tiled ASCII picture of one or more graphs.

    Args:
        g: Single graph or list of graphs to render.
        color: Color style or list of styles (one per graph).
        nodelabel: Node attribute key for display labels.
        edgelabel: Edge attribute key for display labels.
        size: Canvas size passed to ``nx_to_ascii``.
        debug: Directory path for ``.dot`` debug output.
        pos: Pre-computed node positions.
        zoomlevel: Hop distance for zoom subgraph extraction.
        zoomnodes: Nodes around which to zoom (per graph).
        n_graphs_per_line: Number of graphs per row in tiled output.

    Returns:
        Tiled ASCII string of all graphs.
    """



    # everything musst be lists:
    if not isinstance(g, list):
        g = [g]
        color = [color]
        zoomnodes= [zoomnodes]
    else:
        # g is already a list
        if not isinstance(color, list):
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


def do_zoom(gr: nx.Graph, zoomlevel: int, no: list[Any]) -> nx.Graph:
    """Return a subgraph of nodes within ``zoomlevel`` hops of ``no``.

    Args:
        gr: Source graph.
        zoomlevel: Maximum shortest-path distance from zoom nodes.
        no: List of center nodes to zoom around. Returns the full graph
            if empty.

    Returns:
        Subgraph containing only nodes within the zoom radius.
    """
    if not no:
        return gr
    oklist = [a for (a, b) in short_paths(gr,no, zoomlevel)]
    return gr.subgraph(oklist)

#################################
#  down here is utility stuff
#################################

def makerows(graph_canvazes: list[str], n_graphs_per_line: int = 5) -> str:
    """Arrange multiple ASCII graph canvases into side-by-side rows.

    Args:
        graph_canvazes: List of multi-line ASCII strings (one per graph).
        n_graphs_per_line: Maximum graphs per output row.

    Returns:
        Single multi-line string with graphs tiled horizontally.
    """

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

def gprint(g: nx.Graph | list[nx.Graph], **kwargs: Any) -> None:
    """Print the ASCII picture of a graph (or list of graphs).

    Args:
        g: Graph or list of graphs to print.
        **kwargs: Additional keyword arguments forwarded to ``make_picture``.
    """
    print(make_picture(g, **kwargs))

def ginfo(g: nx.Graph) -> None:
    """Print node and edge attributes of a graph.

    Args:
        g: NetworkX graph to inspect.  ``asciisymbol`` attributes are
            stripped before printing.
    """
    for n,d in g.nodes(data=True):
        d.pop('asciisymbol',None)
        print (n,)
        pprint (d)
    for a,b,d in g.edges(data=True):
        d.pop('asciisymbol',None)
        print (a,b,)
        pprint (d)
