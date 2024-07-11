from qgis.core import (QgsProject,
                       QgsLineString,
                       QgsFeature,
                       QgsGeometry,
                       QgsPointXY,
                       QgsVectorLayer,
                       QgsLineSymbol
                       )

def make_vector(course_df):
    vl = QgsVectorLayer(course_df.to_json(),"output","ogr")
    QgsProject.instance().addMapLayer(vl)
    
