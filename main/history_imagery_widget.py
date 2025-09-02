# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               HistoryImageryDockWidget
 select historical imagery dialog.

        begin                : 2025-09-01
        copyright            : (C) 2025 by phoenix-gis
        email                : phoenixgis@sina.com
        website              : phoenix-gis.cn
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

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsNetworkAccessManager

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/HistoryImageryDockWidget.ui'))

class HistoryImageryDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(HistoryImageryDockWidget, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface

        canvas = iface.mapCanvas()
        canvas.extentsChanged.connect(self.on_extents_changed)

        self.networkManager = QgsNetworkAccessManager.instance()

    def on_extents_changed(self):
        # get central coordinate.
        map_extent = self.iface.mapCanvas().extent()
        # print(f"central coordinate: {center.x()}, {center.y()}")
        # transform coordinate from current project to EPSG:4326
        current_project_crs = QgsProject.instance().crs()
        coord_trans = QgsCoordinateTransform(
            current_project_crs,
            QgsCoordinateReferenceSystem("EPSG:4326"),
            QgsProject.instance(),
        )

        map_center_in_4326 = coord_trans.transform(map_extent)
        self.update_layers(map_center_in_4326)

    def update_layers(self, view_extent):
        # nothing to update.
        pass
