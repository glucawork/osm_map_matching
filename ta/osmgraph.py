"""
Read graphs in Open Street Maps osm format

Based on osm.py from brianw's osmgeocode
http://github.com/brianw/osmgeocode, which is based on osm.py from
comes from Graphserver:
http://github.com/bmander/graphserver/tree/master and is copyright (c)
2007, Brandon Martin-Anderson under the BSD License
"""


import xml.sax
import copy
import networkx
import geopy.distance as distance
import geopy.point as point
from . import geoutils
import string

distance = distance.GreatCircleDistance

# Convert a path (list of nodes) in a list of edges
def path2edgelist( path ):
    ret = []
    for i in range(len(path)-1):
        ret.append((path[i],path[i+1]))
    return ret

# convert a Node into Point
def node2point(G, node):
    return point.Point(longitude=G.nodes[node]['data'].lon,
                     latitude=G.nodes[node]['data'].lat)

# Compute the closer edge to gpxpoint in G. Returns the closer node in this edge.
def closerNodeCloserEdge(G, gpxpoint):
    mindist = -1
    ret = None
    for e in G.edges():
        t1 = node2point(G, e[0])
        t2 = node2point(G, e[1])
        newdist = geoutils.pointEdgeDist(t1, t2, gpxpoint).meters
        if mindist == -1 or newdist < mindist:
            mindist = newdist
            if distance(t1, gpxpoint) < distance(t2, gpxpoint):
                ret = e[0]
            else:
                ret = e[1]
    return (ret,mindist)

# Return the closer node  in the nodelist tu the point p
def closerNode(G, nodelist, p):
    mindist = -1
    for v in nodelist:
        vp = node2point(G, v)
        if mindist == -1 or distance(vp, p) < mindist:
            mindist = distance(vp, p)
            ret = v
    return ret

def closerNodeCloserEdgeInPath(G, paths, gpxpoint):
    mindist = -1
    ret = None
    for target in paths.keys():
        if len(paths[target]) == 1:
            t = node2point(G, paths[target][0]);
            newdist = distance(t, gpxpoint).meters
            if mindist == -1 or newdist < mindist:
                ret = paths[target][0]
        else:
            edgelist = path2edgelist( paths[target] )
            for e in edgelist:
                t1 = node2point(G, e[0])
                t2 = node2point(G, e[1])
                newdist = geoutils.pointEdgeDist(t1, t2, gpxpoint).meters
                if mindist == -1 or newdist < mindist:
                    mindist = newdist
                    if distance(t1, gpxpoint) < distance(t2, gpxpoint):
                        ret = e[0]
                    else:
                        ret = e[1]
    return (mindist, ret)
    
def closerNodeCloserEdgeInPathNew(G, edges, gpxpoint):
    mindist0, mindist1, ret = None, None, None
    
    # mindist0 and mindist1 represent the distance to the nearest edge
    # and the distance to the next furthest edge, respectively.
    #
    # If mindist0 and mindist1 are similar, the node should be ignored.

    
    
    sorted_edges = sorted(edges, key=lambda e: geoutils.pointEdgeDist(node2point(G, e[0]), node2point(G, e[1]), gpxpoint).meters)

    emin = sorted_edges[0]
    mindist0 = geoutils.pointEdgeDist(node2point(G, emin[0]) ,node2point(G, emin[1]), gpxpoint).meters
    if distance(node2point(G, emin[0]), gpxpoint) < distance(node2point(G, emin[1]), gpxpoint):
        ret = emin[0]
    else:
        ret = emin[1]
    
    for e in sorted_edges[1:]:
        if e[0] != emin[0] and e[1] != emin[0] and e[0] != emin[1] and e[1] != emin[1]: # not adjacent with emin
            mindist1 = geoutils.pointEdgeDist(node2point(G, e[0]), node2point(G, e[1]), gpxpoint).meters
            break
    
    return (mindist0, mindist1, ret)
    
def closerNodeCloserEdgeInPath3(G, edges, dist, gpxpoint, dist_pq):
    mindist0, mindist1, ret = None, None, None
    
    # mindist0 and mindist1 represent the distance to the nearest edge
    # and the distance to the next furthest edge, respectively.
    #
    # If mindist0 and mindist1 are similar, the node should be ignored.

    
    def w( e, c = 0.1 ):
        closest_node = e[0] if distance(node2point(G, e[0]), gpxpoint) < distance(node2point(G, e[1]), gpxpoint) else e[1]
        return geoutils.pointEdgeDist(node2point(G, e[0]) ,node2point(G, e[1]), gpxpoint).meters + c*abs(dist[closest_node] - dist_pq)

    sorted_edges = sorted(edges, key=w)
    emin = sorted_edges[0]
    mindist0 = geoutils.pointEdgeDist(node2point(G, emin[0]) ,node2point(G, emin[1]), gpxpoint).meters
    
    if distance(node2point(G, emin[0]), gpxpoint) < distance(node2point(G, emin[1]), gpxpoint):
        ret = emin[0]
    else:
        ret = emin[1]
    
    for e in sorted_edges[1:]:
        if e[0] != emin[0] and e[1] != emin[0] and e[0] != emin[1] and e[1] != emin[1]: # not adjacent with emin
            mindist1 = geoutils.pointEdgeDist(node2point(G, e[0]), node2point(G, e[1]), gpxpoint).meters
            break
    
    return (mindist0, mindist1, ret)


# Add the attribute 'w' on the edges of G. 'w' is the lenght of the edge
# expressed in meters
def addEdgeWeights(G):
    for e in G.edges():
        t1 = point.Point(longitude=G.nodes[e[0]]['data'].lon,
                     latitude=G.nodes[e[0]]['data'].lat)
        t2 = point.Point(longitude=G.nodes[e[1]]['data'].lon,
                     latitude=G.nodes[e[1]]['data'].lat)
        G[e[0]][e[1]]['w'] = distance(t1, t2).meters

def addEdgeWeight(G, e):
    t1 = point.Point(longitude=G.nodes[e[0]]['data'].lon,
                 latitude=G.nodes[e[0]]['data'].lat)
    t2 = point.Point(longitude=G.nodes[e[1]]['data'].lon,
                 latitude=G.nodes[e[1]]['data'].lat)
    G[e[0]][e[1]]['w'] = distance(t1, t2).meters

def pathLenght(G, path):
    d = 0
    for i in range(len(path)-1):
        d = d + distance(node2point(G, path[i]),node2point(G, path[i+1])).meters
    return d


def ToOverpassQl(s):
    ns = ''
    
    for x in s:
        if x in string.punctuation + ' ' and x != '"' and x != '~':
            ns += '%'+hex(ord(x))[2:]
        else:
            ns += x
            
    ns += '&0A'
    return ns

def download_osm(left,bottom,right,top):
    """ Return a filehandle to the downloaded data."""
    from urllib.request import urlopen
    #fp = urlopen( "http://api.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f"%(left,bottom,right,top) )
    
    #urlstring = "http://overpass-api.de/api/map?bbox=%f,%f,%f,%f"%(left,bottom,right,top)
    #fp = urlopen( urlstring )
    #print(urlstring)
    
    #fp = urlopen( "http://www.overpass-api.de/api/xapi?way[bbox=%f,%f,%f,%f][highway=*]"%(left,bottom,right,top) )
    
    #overpasquery = "(node(%f,%f,%f,%f);way(%f,%f,%f,%f);node(w)->.x;);out;"%(bottom,left,top,right,bottom,left,top,right)
    overpasquery = "(way[\"highway\"~\".\"](%f,%f,%f,%f);node(w)->.x;);out body;"%(bottom,left,top,right)
    overpassstring = ToOverpassQl(overpasquery)
    urloverpass = "http://overpass-api.de/api/interpreter?data="+overpassstring
    #urloverpass = "https://overpass.openstreetmap.ru/api/interpreter?data="+overpassstring
    #print(urloverpass)
    fp = urlopen( urloverpass )
    return fp

def read_osm(filename_or_stream, only_roads=True):
    """Read graph in OSM format from file specified by name or by stream object.

    Parameters
    ----------
    filename_or_stream : filename or stream object

    Returns
    -------
    G : Graph

    Examples
    --------
    >>> G=nx.read_osm(nx.download_osm(-122.33,47.60,-122.31,47.61))
    >>> plot([G.node[n]['data'].lat for n in G], [G.node[n]['data'].lon for n in G], ',')

    """
   
    osm = OSM(filename_or_stream)
    
    G = networkx.Graph()
    
 

    for w in osm.ways.values():
        if only_roads and 'highway' not in w.tags:
            continue
        # excludes some highways
#        if w.tags['highway'] in  ["motorway", "trunk", "primary", "steps"]:
#            continue
#        if w.tags['highway'] == 'path' and not w.tags.has_key('mtb:scale'):
#            continue
#        if w.tags['highway'] == 'path' and int(w.tags['mtb:scale']) >0:
#            continue
        
        networkx.add_path(G, w.nds, id=w.id, data=w)
   
    for n_id in G.nodes():
        n = osm.nodes[n_id]
        G.nodes[n_id].update(dict(data=n))
    return G
        
    
class Node:
    def __init__(self, id, lon, lat):
        self.id = id
        self.lon = lon
        self.lat = lat
        self.ele = 0
        self.dummy = False
        self.tags = {}
        
class Way:
    def __init__(self, id, osm):
        self.osm = osm
        self.id = id
        self.nds = []
        self.tags = {}
        
    def split(self, dividers):
        # slice the node-array using this nifty recursive function
        def slice_array(ar, dividers):
            for i in range(1,len(ar)-1):
                if dividers[ar[i]]>1:
                    #print "slice at %s"%ar[i]
                    left = ar[:i+1]
                    right = ar[i:]
                    
                    rightsliced = slice_array(right, dividers)
                    
                    return [left]+rightsliced
            return [ar]
            
        slices = slice_array(self.nds, dividers)
        
        # create a way object for each node-array slice
        ret = []
        i=0
        for slice in slices:
            littleway = copy.copy( self )
            littleway.id += "-%d"%i
            littleway.nds = slice
            ret.append( littleway )
            i += 1
            
        return ret
        
        

class OSM:
    def __init__(self, filename_or_stream):
        """ File can be either a filename or stream/file object."""
        nodes = {}
        ways = {}
        
        superself = self
        
        class OSMHandler(xml.sax.ContentHandler):
            @classmethod
            def setDocumentLocator(self,loc):
                pass
            
            @classmethod
            def startDocument(self):
                pass
                
            @classmethod
            def endDocument(self):
                pass
                
            @classmethod
            def startElement(self, name, attrs):
                if name=='node':
                    self.currElem = Node(attrs['id'], float(attrs['lon']), float(attrs['lat']))
                elif name=='way':
                    self.currElem = Way(attrs['id'], superself)
                elif name=='tag':
                    self.currElem.tags[attrs['k']] = attrs['v']
                elif name=='nd':
                    self.currElem.nds.append( attrs['ref'] )
                
            @classmethod
            def endElement(self,name):
                if name=='node':
                    nodes[self.currElem.id] = self.currElem
                elif name=='way':
                    ways[self.currElem.id] = self.currElem
                
            @classmethod
            def characters(self, chars):
                pass

        xml.sax.parse(filename_or_stream, OSMHandler)
    
        self.nodes = nodes
        self.ways = ways
            
        #count times each node is used
        node_histogram = dict.fromkeys( self.nodes.keys(), 0 )
        for way in self.ways.values():
            if len(way.nds) < 2:       #if a way has only one node, delete it out of the osm collection
                del self.ways[way.id]
            else:
                for node in way.nds:
                    node_histogram[node] += 1
        
        #use that histogram to split all ways, replacing the member set of ways
        new_ways = {}
        for id, way in self.ways.items():
            split_ways = way.split(node_histogram)
            for split_way in split_ways:
                new_ways[split_way.id] = split_way
        self.ways = new_ways
