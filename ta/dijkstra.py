import heapq
from . import osmgraph as osm
import geopy.distance as distance

distance = distance.GreatCircleDistance


# returns the shortest paths towards all nodes with a neighbor at distance
# not greater than cutoff
def single_source_dijkstra(G,source, cutoff,weight='weight'):
    """Compute shortest paths and lengths in a weighted graph G.

    Uses Dijkstra's algorithm for shortest paths.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    target : node label, optional
       Ending node for path

    cutoff : integer or float, optional
       Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    distance,path : dictionaries
       Returns a tuple of two dictionaries keyed by node.
       The first dictionary stores distance from the source.
       The second stores the path from the source to that node.


    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> length,path=nx.single_source_dijkstra(G,0)
    >>> print(length[4])
    4
    >>> print(length)
    {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
    >>> path[4]
    [0, 1, 2, 3, 4]

    Notes
    ---------
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    Based on the Python cookbook recipe (119466) at
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/119466

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems).

    See Also
    --------
    single_source_dijkstra_path()
    single_source_dijkstra_path_length()
    """
    
    alledges = []
    dist = {}  # dictionary of final distances
    paths = {source:[source]}  # dictionary of paths
    seen = {source:0}
    fringe=[] # use heapq with (distance,label) tuples
    heapq.heappush(fringe,(0,source))
    # nodes out of cutoff but with predecessor inside
    borderline = [] 
    while fringe:
        (d,v)=heapq.heappop(fringe)
        if v  in dist:
            continue # already searched this node
        dist[v] = d

        if v in borderline:
            continue # node outside cutoff

        #for ignore,w,edgedata in G.edges_iter(v,data=True):
        #is about 30% slower than the following
        if G.is_multigraph():
            edata=[]
            for w,keydata in G[v].items():
                minweight=min((dd.get(weight,1)
                               for k,dd in keydata.items()))
                edata.append((w,{weight:minweight}))
        else:
            edata=iter(G[v].items())

        for w,edgedata in edata:
            vw_dist = dist[v] + edgedata.get(weight,1)
            if cutoff is not None:
                #if vw_dist>cutoff:
                if distance(osm.node2point(G, source), osm.node2point(G, w)).meters > cutoff:
                    borderline.append(w)
            if w in dist:
                if vw_dist < dist[w]:
                    raise ValueError('Contradictory paths found:',
                                     'negative weights?')
            elif w not in seen or vw_dist < seen[w]:
                seen[w] = vw_dist
                heapq.heappush(fringe,(vw_dist,w))
                paths[w] = paths[v]+[w]
                alledges.append((v,w))
    return (dist,paths,alledges)
