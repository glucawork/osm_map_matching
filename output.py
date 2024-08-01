from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsLineString,
    QgsFields,
    QgsWkbTypes,
    QgsProject
)
from PyQt5.QtCore import QVariant
import json

def make_vector(dizionario_list):
    # Creare il layer vettoriale con tipo geometrico LineString
    layer = QgsVectorLayer('LineString?crs=EPSG:4326', 'Linestrings Layer', 'memory')
    provider = layer.dataProvider()
    
    # Definire i campi (attributi) del layer
    fields = QgsFields()
    
    # Aggiungere campi in base agli attributi nei dizionari
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
    
    # Aggiungere le features al layer
    for diz in dizionario_list:
        feature = QgsFeature()
        # Creare la geometria LineString
        linestring = diz.get('geometry')
        if linestring:
            points = [QgsPointXY(point[0], point[1]) for point in linestring]
            geometry = QgsGeometry.fromPolylineXY(points)
            feature.setGeometry(geometry)
        
        # Impostare gli attributi della feature
        list_of_attributes = [diz.get('osm_id', '')]
        
        for tag in list_of_tags:
            list_of_attributes.append(diz['tags'].get(tag, ''))
        
        feature.setAttributes(list_of_attributes)
        
        # Aggiungere la feature al provider
        provider.addFeatures([feature])
    
    # Aggiornare l'estensione del layer
    layer.updateExtents()
    
    QgsProject.instance().addMapLayer(layer)
    
