# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AMapExtension
                                 SelectedAreaDrawer
 provide drawing a rectangle on the QGIS map canvas.
                              -------------------
        begin                : 2025-09-06
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

from qgis.gui import QgsMapCanvasItem
from qgis.core import QgsRectangle, QgsPointXY
from qgis.PyQt.QtCore import Qt, QRectF
from qgis.PyQt.QtGui import QColor, QPen

class SelectedAreaDrawer(QgsMapCanvasItem):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.area = None

    def set_area(self, area : QgsRectangle):
        self.area = area

    def clear(self):
        self.area = None

    def paint(self, painter, option, widget):
        if self.area is None:
            return
        # convert from coordinates to canvas position.
        top_left = QgsPointXY(self.area.xMinimum(), self.area.yMaximum())
        bottom_right = QgsPointXY(self.area.xMaximum(), self.area.yMinimum())

        top_left_in_pixel = self.toCanvasCoordinates(top_left)
        bottom_right_pixel = self.toCanvasCoordinates(bottom_right)

        rect_in_pixel = QRectF(top_left_in_pixel, bottom_right_pixel)

        # set yellow pen
        painter.setPen(QPen(QColor(255, 255, 0)))
        painter.setBrush(Qt.NoBrush)  # without filling
        painter.drawRect(rect_in_pixel)
