#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Created on Fri Apr 11 11:23:38 2014

@author: gianluca
"""

import networkx as nx
from . import osmgraph as osm
from .dijkstra import single_source_dijkstra
import geopy.distance as distance
import sys
from geopy.point import Point

sys.setrecursionlimit(1500)


distance = distance.GreatCircleDistance

offlineMode = False


def boundBBox( gt, startindex, addpoint = None ):
    '''

    Parameters
    ----------
    gt : list of Point
    startindex :an integer denoting the starting  point for the search
    addpoint : an additional point that must to be included
    #				   to be included in the bounding box

    Returns
    -------
    (left, botton, right, top, next) - if next == -1 (left, botton, right, top)
    #			is the bounding box containing gt.trkpoint[startindex:] otherwise
    #		   is the bounding box containing gt.trkpoint[startindex:next].
    #		   in any case the area of the bounding box is at most 50km^2

    '''
    maxarea = 1000000 # 1km^2 in meters
    currentarea = 0
	
    procpoints = 0
	
    if addpoint != None:
	    p = Point(latitude = addpoint[0], longitude = addpoint[1])
	    nextindex = startindex
    else:
        p = gt[startindex]
        nextindex = startindex + 1

    left = p.longitude
    right = p.longitude
    bottom = p.latitude
    top = p.latitude
		
    while nextindex < len(gt) and currentarea < maxarea:# and procpoints < 200:
        p = gt[nextindex]
        if p.longitude > right:
            right = p.longitude
        elif p.longitude < left:
            left = p.longitude
        if p.latitude > top:
            top = p.latitude
        elif p.latitude < bottom:
            bottom = p.latitude
        currentarea = distance(Point(left, top), Point(left, bottom)).meters * distance(Point(left, bottom), Point(right, bottom)).meters
        nextindex += 1
        procpoints +=1

    dlon =  (right-left)/10
    dlat =  abs(abs(top)-abs(bottom))/10

    if nextindex == len(gt):
        nextindex = -1
		
    return (left-dlon, bottom-dlat, right+dlon, top+dlat, nextindex)


def analyze(points_list, max_dist, min_loop_size, feedback = None):
    '''
    Parameters
    ----------
    points_list : list of geopy points

    Returns
    -------
    
    G, p where
        G is a networkx graph that represents the road network
        path is a list of nodes in G that represents the output path
    
    If something goes wrong, it returns None, None.
    '''
    
    def PrintMessage( m ):
        if feedback != None:
            feedback.pushInfo(str(m))
    
    def remove_loops(path):
        '''
        Parameter: path list of nodes
        Output: clean_path, a list of nodes without loop of size smaller than
            max_loop_size
        '''
        def find(a, p, e):
            dist = 0
            while p < len(a):
                if a[p] == e:
                    return p, dist
                dist += distance(osm.node2point(G, a[p-1]), osm.node2point(G, a[p])).meters
                p += 1
            return -1, None
        
        if len(path) == 0:
            return path
        
        repeat = True
        
        while repeat:
            repeat = False
            clean_path = []
            i = 0
            n_points = 100.0 / len(path) if len(path) > 0 else 0
            while i < len(path):
                if feedback != None:
                    feedback.setProgress(int(i * n_points))
                x = path[i]
                if clean_path == [] or x != clean_path[-1]:
                    clean_path.append(x)
                    j,d = find(path, i+1, x)
                    if j >= 0 and d < min_loop_size:
                        i = j
                        # This loop might be contained in a larger one.
                        # In the next iteration, we will check if this needs to be removed
                        repeat = True
                i += 1
            path = clean_path
            if feedback.isCanceled():
                PrintMessage('Cleaning interrupted')
                break
            
        return path

    # -------- Computing bounding box
    left,bottom,right,top, nextindex  = boundBBox(points_list, 0)
    
    # -------- Downloading OSM data

    try:
        if offlineMode:
            pass
            # TODO
        else:
            osmmap = osm.download_osm(left, bottom, right, top)
    except:
        PrintMessage('Error in downloading OSM data')
        return None, None

    #-------- Computing map graph

    try:    
        Gp = osm.read_osm(osmmap)
    except:
        PrintMessage('Error in building map graph')
        return None, None
    

    if feedback != None:
        n_points = 100.0 / len(points_list) if len(points_list) > 0 else 0


    # The graph: G.edge[u][v] = {data:tags, id:wayid-num}
    
    osm.addEdgeWeights(Gp)

    path = []
    
    dummypath = False
    dummypath_number = 0
    

    
    p =  points_list[0]
    startnode,mindist = osm.closerNodeCloserEdge(Gp, p)
    
    if mindist > max_dist:
        # it is created a dummy starting node
         startnode = 'unrec'+str(p.longitude)+str(p.latitude)
         Gp.add_node(startnode)
         Gp.nodes[startnode].update(dict(data=osm.Node(startnode, p.longitude, p.latitude)))
         Gp.nodes[startnode]['data'].dummy = True
         dummypath = True
         
    path.append(startnode)

    # Gp is the small graph used to compute the path, G is the hole graphs
    # obtained by joining all the Gp
    G = nx.Graph()
    
    # -------- Computing sub-path

    # the matching path is a list of osm nodes or dummy nodes
    # a dummy node is added if the "matching node" is to far
    # from the track node
    for i in range(1, len(points_list)):
        if feedback != None:
            feedback.setProgress(int(i * n_points))
        if nextindex == -1 or i < nextindex:
            p = points_list[i]
            
            dd = distance(osm.node2point(Gp, startnode), p).meters
            
            if dummypath:
                startnode,mindist = osm.closerNodeCloserEdge(Gp, p)
            else:
                (dist,shortestpaths,alledges) = single_source_dijkstra(Gp, startnode,\
                    max(max_dist, 1.5*distance(osm.node2point(Gp, startnode), p).meters), weight='w')
                x = startnode
                if alledges == []:
                    mindist, mindist1 = 0, 0
                else:
                    (mindist, mindist1, startnode) = osm.closerNodeCloserEdgeInPathNew(Gp, alledges,  p )
                
                if mindist1 != None and abs(mindist-mindist1) < 3:
                    startnode = x
                    continue
            # while mindist > max_dist we create an unrecognized segment composed
            # by new dummy nodes added to the graph
            if mindist < 0 or mindist > max_dist:
                startnode = 'unrec'+str(p.longitude)+str(p.latitude)
                Gp.add_node(startnode)
                Gp.nodes[startnode].update(dict(data=osm.Node(startnode, p.longitude, p.latitude)))
                Gp.nodes[startnode]['data'].dummy = True
                newedge = (path[-1], startnode)         
                Gp.add_edge(newedge[0], newedge[1])
                osm.addEdgeWeight(Gp, newedge)
                path.append(startnode)
                dummypath = True
            else:
                if dummypath:
                    newedge = (path[-1], startnode)         
                    Gp.add_edge(newedge[0], newedge[1])
                    osm.addEdgeWeight(Gp, newedge)
                    path.append(startnode)
                else:
                    path.extend( shortestpaths[startnode] )
                    
                dummypath = False
        else:

            #downloading next osm data area
            # "-------- Computing bounding box")
            try:
                ( left,bottom,right,top, nextindex ) = boundBBox(points_list, nextindex, (Gp.nodes[startnode]['data'].lat, Gp.nodes[startnode]['data'].lon) )
            except:
                PrintMessage('Empty vector')
                return None, None
                
            
            # ................", left,bottom,right,top, '-', nextindex)
            
            #-------- Downloading OSM data")
            
            try:
                osmmap = osm.download_osm(left, bottom, right, top)
                PrintMessage("Download new map")
            except:
                PrintMessage('Error in downloading OSM data')
                return None, None
            
            #"-------- Computing map graph")
            
            try:    
                G = nx.compose(G, Gp)
                Gp = osm.read_osm(osmmap)
                # if the last node in path is dummy, in order to avoid
                # problems with the first edge of new section
                # it must be added in Gp
                PrintMessage("Updating graph with new dowloaded data")
                if G.nodes[path[-1]]['data'].dummy :
                    Gp = nx.compose(G, Gp)
                    
                    #lndata = G.nodes[path[-1]]
                    #Gp.add_node(path[-1])
                    #Gp.nodes[path[-1]].update(lndata)
            except:
                PrintMessage('Error in bouilding map graph')
                return None, None
            #-------- Computing sub-path")
    
    G = nx.compose(Gp, G)

    #"===== Cleaning path")

    # removing consecutive duplicates
    
    PrintMessage("Press 'Cancel' to skip this part")
    path = remove_loops(path)
    
    return G, path



def make_out_dataframe(G, path, log=None):
    linestrings = []
    current_linestring = {}
    points = []
    next_dummypath_id = 0
    for p,q in zip( path[:-1], path[1:] ):
        again = True
        while again:
            again = False
            try:
                way_id = str(G.edges[p, q]['data'].id).split('-')[0]
            except KeyError: # a dummy edge
                way_id = None
            if current_linestring == {}:
                current_linestring['osm_id'] = way_id
                if way_id != None:
                    current_linestring['tags'] = G.edges[p, q]['data'].tags
                points.extend( [ [G.nodes[p]['data'].lon, G.nodes[p]['data'].lat], [G.nodes[q]['data'].lon, G.nodes[q]['data'].lat] ] )
            elif way_id == current_linestring['osm_id']:
                points.append( [ G.nodes[q]['data'].lon, G.nodes[q]['data'] .lat ] )
            else:
                current_linestring['geometry'] = points
                linestrings.append(current_linestring)
                current_linestring = {}
                points = []
                again = True # repeat for the same p and q
    
    current_linestring['geometry'] = points
    linestrings.append(current_linestring)
        
    #out_gdf = gpd.GeoDataFrame(linestrings)    
    return linestrings
