# StructOut

prints networkx graphs and large int lists pleasantly to terminal. 



```python

import structout as so
so.lprint(range(1000),length=70)

import networkx as nx
g=nx.path_graph(5)
so.gprint(g)

```

![''](https://raw.githubusercontent.com/smautner/StructOut/master/example.png)

## numberlists 

```

# implemented options: -> i should update this at some point :)
def doALine(values,
        length=-1,minmax=False, chunk_operation=max, 
        method = 'log', methodhow =2)

# there is also a convenience function 'bins' that 
# does evenly spaced out bins :) 

```

## Graphs

### Colors

```python
# this will color nodes 1,2,3 in one color and 4,0 in another
gprint(graph, color=([1,2,3],[4,0]))
```

-  edge labels are always blue
-  digraphs should mark the direction with a blue dot 

### cut graph down to a subgraph 

```python
# print nodes with max distance 1 to the nodes 1 and 2 
gprint(graph, zoomlevel=1, zoomnodes=[1,2]) 
```


### other options 

```python
nodelabel='label',  # node and edge labels
edgelabel='label',
size=10,            # size
pos=None,           # pass a coordinate dictionary ; {nodeid : x,y} 
n_graphs_per_line= 5 # when passing multiple graphs, wrap here
```

