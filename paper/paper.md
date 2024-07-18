---
title: 'osm_map_matching: a QGIS plugin that calculates a match between a vector of points and OSM highways'
tags:
  - qgis plugin
  - map-matching
  - openstreetmap
  - python
authors:
  - name: Gianluca Rossi
    orcid: 0000-0002-6440-8203
    equal-contrib: true
affiliations:
 - name: Università di Tor Vergata - Roma, Italy
date: 12 July 2024
bibliography: paper.bib

---

# Summary

In the map-matching problem, a sequence of geographic positions, typically obtained from GPS data, must be aligned with the routes depicted in a digital map. The aim is to accurately determine the most likely route taken by a moving object, such as a vehicle or pedestrian, by matching the observed data points with the roads or pathways described by the map.

`osm-map-matching` is a Python-based QGIS plugin [@QGIS] designed to match an input vector layer of observed geographic positions with corresponding routes from OpenStreetMap [@OSM]. The output is a vector layer containing linestrings that represent the matched routes. Each linestring in the vector corresponds to a continuous segment characterized by consistent features extracted from the map data.

The solution used employs a topology-based algorithm that calculates the shortest path from points in the road network that have specific proximity characteristics to the input points. This resulting algorithm is significantly faster than others [@Duffield2022, @Jung2019] without sacrificing the quality of the solutions.

# Statement of need

As far as we know there exist two map matching plugin for QGIS, *Offline-MapMatching* [@Jung2019] and , *Assisted-MapMatching* [@Gelb]. 

The two plugins are based on Hidden Markov Models, known for their high time complexity [@newson2009hidden], resulting in long execution times. Our plugin's algorithm computes, for each input point $p$, the shortest-path tree of a small region centered around $p$, significantly improving its practical speed.

Additionally, we were unable to fully get the two plugins to work, possibly due to lack of maintenance as they have not been updated in the past two years.

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements


# References
