# -*- coding: utf-8 -*-
"""
Created on Fri Apr 11 19:02:34 2014

@author: gianluca
"""

import geopy.point as point
import geopy.distance
import math

def geometricDist2( p1, p2 ):
    return math.pow(p1.longitude - p2.longitude, 2) + math.pow(p1.latitude - p2.latitude, 2)

def pointEdgeDist(e1, e2, p): # dist from p and (e1, e2)
    distance = geopy.distance.GreatCircleDistance
    l2 = geometricDist2(e1, e2)
    if l2 == 0.0:
        return distance(e1, p)
    t = ((p.longitude - e1.longitude)*(e2.longitude-e1.longitude)+(p.latitude - e1.latitude)*(e2.latitude-e1.latitude))/l2
    if t < 0:
        return distance(p, e1)
    if t > 1:
        return distance(p, e2)
    pp = point.Point(latitude=e1.latitude+t*(e2.latitude-e1.latitude),
                     longitude=e1.longitude+t*(e2.longitude-e1.longitude))
    return distance(p, pp)