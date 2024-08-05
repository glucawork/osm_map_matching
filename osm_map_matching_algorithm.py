# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Osm Map Matching
                                 A QGIS plugin
 Plugin che fa qualche cosa
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-07-26
        copyright            : (C) 2023 by G.Rossi
        email                : grossi@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'G.Rossi'
__date__ = '2023-07-26'
__copyright__ = '(C) 2023 by G.Rossi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterVectorDestination,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsProject)
from qgis.core import QgsMessageLog

from geopy.point import Point


from .ta import main as ta
from . import output

class OsmMapMatchingAlgorithm(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    VPOINTS = 'VECTOR_POINTS'
    MAXDIST = 'MAXDIST'
    MINLOOPSIZE = "MINLOOPSIZE"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VPOINTS,
                self.tr('Vector Points'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # the maximum tolerated distance between the point and the map
        # self.addParameter(
            # QgsProcessingParameterDistance(
                # self.MAXDIST,
                # self.tr('Max distance from map point'),
                # 30
            # )
        # )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAXDIST,
                self.tr('Max distance from map point (meters)'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=30.0
            )
        )
        
        # # shorter loop are removed
        # self.addParameter(
            # QgsProcessingParameterDistance(
                # self.MINLOOPSIZE,
                # self.tr('Min loop size'),
                # 15
            # )
        # )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MINLOOPSIZE,
                self.tr('Minimum loop size (meters)'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=15.0
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Output File'),
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.VPOINTS, context)
        output_layer = self.parameterAsLayer(parameters, self.OUTPUT, context)
        max_dist = self.parameterAsDouble(parameters, self.MAXDIST, context)
        min_loop_size = self.parameterAsDouble(parameters, self.MINLOOPSIZE, context)
        
        #fieldnames = [field.name() for field in source.fields()]

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()        
        
        # the point must be reprojevted in EPSG:4326
        source_crs = QgsCoordinateReferenceSystem(source.sourceCrs().authid())
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")

        feedback.pushInfo('Vector reading')

        points_list = []

        for current, f in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            p = f.geometry().asPoint()
            
            geom = f.geometry()
            geom.transform(QgsCoordinateTransform(source_crs, target_crs, QgsProject.instance()))
            p = geom.asPoint()
             
            points_list.append(Point(latitude=p.y(), longitude=p.x()))

            feedback.setProgress(int(current * total))
            
        feedback.pushInfo('Analizing')
        G, path = ta.analyze(points_list, max_dist, min_loop_size, feedback)
        
        if path != None:
            out_df = ta.make_out_dataframe(G, path, log=feedback)
            feedback.pushInfo('Vector output creation')
            output_layer = output.make_vector(out_df)
            QgsProject.instance().addMapLayer(output_layer)
            

        return {self.OUTPUT: output_layer}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Analyze'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '' # 

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return OsmMapMatchingAlgorithm()
