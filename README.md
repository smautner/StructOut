# StructOut

prints networkx graphs and large int lists pleasantly to terminal. 



```python

import structout as so

so.lprint(range(1000),length=70)

so.dprint({x*x:x for x in range(1000) }) # sparse datatype
so.dprint({x*x:x for x in range(1000) }, chunk_operation=len) # count elements oO

import networkx as nx
g=nx.path_graph(5)
so.gprint(g)


```

![''](https://raw.githubusercontent.com/smautner/StructOut/master/example.png)


