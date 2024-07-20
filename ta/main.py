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


#from shapely import LineString as shLineString
#from shapely import Point as shPoint

#import geopandas as gpd

sys.setrecursionlimit(1500)


distance = distance.GreatCircleDistance

offlineMode = False

    
def ErrorExit( message ):
    print(message)
    sys.exit();
    

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


def analyze(points_list, max_dist, feedback = None):
    '''
    Parameters
    ----------
    points_list : list of geopy points

    Returns
    -------
    A networkx graph G from osm and a list of nodes that reprenst the
    matched path of points_df in G
    '''
    


    # -------- Computing bounding box
    left,bottom,right,top, nextindex  = boundBBox(points_list, 0)
    
    # -------- Downloading OSM data

    try:
        if offlineMode:
            osmmap = './ta/osm/camposoriano.osm'
        else:
            osmmap = osm.download_osm(left, bottom, right, top)
        #osmmap = '/home/gianluca/Downloads/map'
    except:
        ErrorExit('Error in downloading OSM data')

    #-------- Computing map graph

    try:    
        Gp = osm.read_osm(osmmap)
    except:
        ErrorExit('Error in building map graph')
    

    if feedback != None:
        n_points = 100.0 / len(points_list) if len(points_list) > 0 else 0


    # The graph: G.edge[u][v] = {data:tags, id:wayid-num}
    
    
    #print left,bottom,right,top
    
    #G = osm.read_osm('../../terracina.osm')
    #G = osm.read_osm(osm.download_osm(left, bottom, right, top))
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
         Gp.node[startnode] = dict(data=osm.Node(startnode, p.longitude, p.latitude))
         Gp.node[startnode]['data'].dummy = True
         dummypath = True
         
    path.append(startnode)

    # Gp is the small graph used to compute the path, G is the hole graphs
    # obtained by joining all the Gp
    G = nx.Graph()
    
    # -------- Computing sub-path

    # the matching path is a list of nodes osm nodes or dummy nodes
    # a dummy node is added if the "matching node" is to far
    # from the track node
    for i in range(1, len(points_list)):
        if feedback != None:
            feedback.setProgress(int(i * n_points))
        if nextindex == -1 or i < nextindex:
            p = points_list[i]
            if dummypath:
                startnode,mindist = osm.closerNodeCloserEdge(Gp, p)
            else:
                (dist,shortestpaths,alledges) = single_source_dijkstra(Gp, startnode, 1.5*distance(osm.node2point(Gp, startnode), p).meters,weight='w')
                x = startnode
                (mindist, mindist1, startnode) = osm.closerNodeCloserEdgeInPathNew(Gp, alledges, p )
                if mindist1 != None and abs(mindist-mindist1) < 3:
                    #print(abs(mindist-mindist1))
                    startnode = x
                    continue
            # while mindist > 50 we create an unrecognized segment composed
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
                    path.append(startnode)
                else:
                    path = path + shortestpaths[startnode]
                dummypath = False
        else:
            feedback.pushInfo('NEXT')

            #downloading next osm data area
            # "-------- Computing bounding box")
            try:
                ( left,bottom,right,top, nextindex ) = boundBBox(points_list, nextindex, (Gp.nodes[startnode]['data'].lat, Gp.nodes[startnode]['data'].lon) )
            except:
                ErrorExit('Empty gpx file')
            
            # ................", left,bottom,right,top, '-', nextindex)
            
            #-------- Downloading OSM data")
            
            try:
                osmmap = osm.download_osm(left, bottom, right, top)
            except:
                ErrorExit('Error in downloading OSM data')
            
            #"-------- Computing map graph")
            
            try:    
                G = nx.compose(G, Gp)
                Gp = osm.read_osm(osmmap)
                # if the last node in path is dummy, in order to avoid
                # problems with the first edge of new section
                # it must be added in Gp
                if G.nodes[path[-1]]['data'].dummy :
                    lndata = G.nodes[path[-1]]
                    Gp.add_node(path[-1])
                    Gp.nodes[path[-1]] = lndata
            except:
                ErrorExit('Error in bouilding map graph')
            #-------- Computing sub-path")
    
    G = nx.compose(Gp, G)

    #"===== Cleaning path")

    cleanpath = []


    # eliminazione candele più corte di 10mt
    if False:
        for u in path:
            if len(cleanpath) == 0 or u != cleanpath[-1]:
                cleanpath.append(u)
    else:
        for i in range(len(path)):
            if i == 0:
                cleanpath.append(path[i])
            else:
                j = len(cleanpath)-1
                while j >= 0 and distance( osm.node2point(G,cleanpath[j]), osm.node2point(G, path[i]) ).meters < 15 and cleanpath[j] != path[i]:
                    j -= 1
                if cleanpath[j] == path[i]:
                    cleanpath = cleanpath[:j+1]
                else:
                    cleanpath.append(path[i])
    
    path = cleanpath
    
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
            
        
    #out_gdf = gpd.GeoDataFrame(linestrings)    
    return linestrings
