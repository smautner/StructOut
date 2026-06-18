# StructOut

Pretty-print data structures in the terminal: networkx graphs as ASCII art, numeric lists as colored sparklines, 2D arrays as heatmaps, and scatter plots using braille characters.

## Install

```
pip install structout
```

## Quick start

```python
import structout as so

# sparkline
so.lprint(range(1000))

# graph
import networkx as nx
g = nx.path_graph(5)
so.gprint(g)
```

## Number lists

### Sparklines

```python
so.lprint(range(1000), ylim=(0, 1000))
```
```
0    |▁▁▁▁▁▁▁▁▁▁▁▂▂▂▂▂▂▂▂▂▂▂▃▃▃▃▃▃▃▃▃▃▃▄▄▄▄▄▄▄▄▄▄▄▅▅▅▅▅▅▅▅▅▅▅▆▆▆▆▆▆▆▆▆▆▆▇▇▇▇▇▇▇▇▇▇▇███████████|999
```

```python
so.lprint(range(1000), log=True)
```
```
0    |▁▂▃▃▃▄▄▄▄▅▅▅▅▅▅▅▆▆▆▆▆▆▆▆▆▆▆▆▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇██████████████████████████████████████|999
```

```python
so.lprint(range(1000), showrange=False)
```
```
▁▁▁▁▁▁▁▁▁▁▁▁▁▂▂▂▂▂▂▂▂▂▂▂▂▃▃▃▃▃▃▃▃▃▃▃▃▃▄▄▄▄▄▄▄▄▄▄▄▄▅▅▅▅▅▅▅▅▅▅▅▅▆▆▆▆▆▆▆▆▆▆▆▆▆▇▇▇▇▇▇▇▇▇▇▇▇█████████████
```

### Full API

```python
render_sparkline(
    values,                # numeric array to visualize
    log=False,             # apply log2 scaling
    chunk_operation=max,   # aggregation function for downsampling
    showrange=True,        # show min/max labels
    symbols='▁▂▃▄▅▆▇█',   # block characters (low to high)
    colors='0467',         # ANSI color codes
    ylim=False,            # fixed y-range as (min, max), or False for auto
    characterlimit=99999,  # max output width
)
```

### 2D arrays

```python
import numpy as np
z = np.random.rand(2, 30)
so.npprint(z)
```

### Dictionary-based input

```python
so.iprint({0: 3, 0.3: 6, 4: 3, 21.4: 0.2})
```

## Graphs

### Basic printing

```python
import networkx as nx

g = nx.path_graph(5)
g.nodes[0]['label'] = 'A'
g.nodes[4]['label'] = 'B'
so.gprint(g)
```
```
                  ..B
                ..
             ..3
           ..
         .2
       ..
     ..
   .1
 ..
.
A
```

### Colors

```python
# color specific node groups
so.gprint(g, color=([0,1,2],[3,4]))
```
```
A.
  ..
    1..
       ..
         2.
           ..
             ..
               3.
                 ..
                   .
                    B
```

```python
# black and white mode
so.gprint(g, color='bw')
```
```
        0
        .
        .
         .
         .
4................
          1..    3
             ..   .
               ....
                  ..
                    2
```

- Edge labels are always blue
- Digraphs mark direction with a blue dot

### Zoom into subgraph

```python
g = nx.path_graph(10)
so.gprint(g, radius=2, zoom_nodes=[5])
```
```
       .5
     ..  .
    .    .
   .6     .
  .       .
  .        .
 .          4.
.             ..
7               ..
                  ..
                    3
```

### Multiple graphs

```python
g1 = nx.path_graph(3)
g1.nodes[0]['label'] = 'X'
g2 = nx.path_graph(3)
g2.nodes[0]['label'] = 'Y'
so.gprint([g1, g2])
```
```
X.                     2.
  ..                     ..
    ..                     ..
      ..                     ..
        ..                     ..
          1.                     1.
            ..                     ..
              ..                     ..
                ..                     ..
                  ..                     ..
                    2                      Y
```

### Options

```python
so.gprint(
    g,
    nodelabel='label',    # node attribute key for labels
    edgelabel='label',    # edge attribute key for labels
    size=10,              # canvas height (width is 2x)
    pos=None,             # pre-computed positions {node: (x, y)}
    n_graphs_per_line=5,  # wrap after this many graphs
)
```

### Graph info

```python
g = nx.path_graph(3)
g.nodes[0]['label'] = 'A'
g.nodes[1]['label'] = 'B'
g[0][1]['label'] = 'e0'
so.ginfo(g)
```
```
0
{'label': 'A'}
1
{'label': 'B'}
2
{}
0 1
{'label': 'e0'}
1 2
{}
```

## Heatmap

```python
import numpy as np
z = np.random.rand(20, 20)
so.heatmap(z)
```

```
heatmap(
    matrix,              # 2D numpy array
    dim=(20, 20),        # target dimensions
    operator=np.max,     # reduction function per block
    wide=True,           # double columns for wider display
    legend=True,         # show color legend
)
```

## Scatter / Braille plots

```python
so.plot([0, 0.5, 2, 3], [1, 2, 5, 4])
```
```
1    |         ⠁   ⠠|5
0    |⡀ ⠄           |3
```

```python
so.plot([1, 2, 3])
```
```
1    |▁▄█|3
```

```python
so.scatter(
    x, y,                # coordinate arrays
    xlim=(),             # x-range, or empty for auto
    ylim=(),             # y-range, or empty for auto
    rows=2,              # braille character rows
    columns=14,          # braille character columns
)
```

## Histogram

```python
so.hist([1,2,3,4,5,6,10,10,10,10], 20)
```
```
1    |⣀⣀⣀⣀⣀⣀⣀⣀⣀⡈|10
```

## RNA secondary structure

```python
import structout as so
from structout.rna import _sequence_dotbracket_to_graph

seq = 'AAAAAAAAGGGGGGGGGGUUUUUUUUUUAAAAAAAAAAAA'
stu = ',,,,((((,,((,,,)),,((,,,)),,((,,)))))),,'

g = _sequence_dotbracket_to_graph(seq, stu)
g.graph['structure'] = stu
so.RNAprint(g)
```
```
                        G.-.G.-.G
                          -.    -
                            G.=.G
                            -   -
                            G.=.G
                            -   -
                            G   G
                            -   -
                            G   U.....             .U
                            -         -.....     .- -
A.-.A.-.A.-.A.-.A.-.A.-.A.-.A               U.-.U   U
                =   =   =   =               =   =   -
        A.-.A.-.A.-.A.-.A.-.A      .U.-.U.-.U.-.U.-.U
                            -    .-
                            A.=.A
                            -   -
                            A.=.A.
                              -.  -.
                                A.-.A
```

## Testing

```
pytest tests/
```
