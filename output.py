from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFields,)
from PyQt5.QtCore import QVariant
import json

def make_vector(dizionario_list):
    # Create the vector layer with LineString geometry type
    layer = QgsVectorLayer('LineString?crs=EPSG:4326', 'Linestrings Layer', 'memory')
    provider = layer.dataProvider()
    
    # Define the layer's fields (attributes)
    fields = QgsFields()
    
    # Add fields based on the attributes in the dictionaries
    fields.append(QgsField('osm_id', QVariant.String))
    
    set_of_tags = set()
    for diz in dizionario_list:
        if diz['osm_id'] != None:
            for tag in diz['tags']:
                set_of_tags.add(tag)
        else:
            set_of_tags.add('dummy')
            diz['tags'] = {'dummy':True}
    
    list_of_tags = list(set_of_tags)
    for tag in list_of_tags:
        fields.append(QgsField(tag, QVariant.String))
    
    provider.addAttributes(fields)
    layer.updateFields()
    
    # Add the features to the layer
    for diz in dizionario_list:
        feature = QgsFeature()
        # Create the LineString geometry
        linestring = diz.get('geometry')
        if linestring:
            points = [QgsPointXY(point[0], point[1]) for point in linestring]
            geometry = QgsGeometry.fromPolylineXY(points)
            feature.setGeometry(geometry)
        
        # Set the feature's attributes
        list_of_attributes = [diz.get('osm_id', '')]
        
        for tag in list_of_tags:
            list_of_attributes.append(diz['tags'].get(tag, ''))
        
        feature.setAttributes(list_of_attributes)
        
        # Add the feature to the provider
        provider.addFeatures([feature])
    
    # Update the layer's extent
    layer.updateExtents()
    
    return layer
    
    
