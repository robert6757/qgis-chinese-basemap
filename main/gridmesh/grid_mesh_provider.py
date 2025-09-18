# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               GridMeshProvider
 An implemented class that provides various types of grids and meshes.

        begin                : 2025-09-18
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
from qgis.PyQt.QtCore import QSize, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox
from qgis.core import QgsProject, QgsSettings, QgsVectorLayer, QgsLineSymbol, QgsFields, QgsField, QgsFeature, QgsGeometry, QgsPointXY

from ..abstract_basemap_provider import AbstractBasemapProvider
from ..global_helper import GlobalHelper

class GridMeshProvider(AbstractBasemapProvider):

    def __init__(self):
        self.grid_mesh_list = [
            "接图表",
            "经纬网",
            "方里网",
            "重要纬线",
        ]
        self.setting_form = None
        self.setting_widget = None
        self.iface = None

        self.layer_fields = QgsFields()
        self.layer_fields.append(QgsField("type", QVariant.String))
        self.layer_fields.append(QgsField("value", QVariant.Double))

    def attach_iface(self, iface):
        self.iface = iface

    def provider_name(self):
        """name of provider is shown on the list widget"""
        return GlobalHelper.tr(u"Grid Mesh")

    def provider_icon(self):
        """icon of provider is shown on the list widget"""
        pass

    def make_setting_widget(self):
        """provide specific settings and basemap template"""
        generated_class, base_class = uic.loadUiType(os.path.join(
            os.path.dirname(__file__), '../../ui/GridMeshSettingWidget.ui'))
        if generated_class is None or base_class is None:
            return None

        # build Qt widget
        self.setting_widget = base_class()
        self.setting_form = generated_class()
        self.setting_form.setupUi(self.setting_widget)
        self.setting_form.listWidget.itemClicked.connect(self.handle_listwidget_item_clicked)

        self.setting_form.listWidget.setIconSize(QSize(160, 160))
        for grid_mesh_name in self.grid_mesh_list:
            icon = QIcon(os.path.join(os.path.dirname(__file__), '../../image/gridmesh/%s.png' % grid_mesh_name))
            self.setting_form.listWidget.addItem(QListWidgetItem(icon, grid_mesh_name))

        # the default is Index Grid(接图表).
        self.setting_form.listWidget.setCurrentRow(1)
        self.setting_form.stackedWidget.setCurrentIndex(1)

        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:1,000,000"), 1000000)
        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:500,000"), 500000)
        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:250,000"), 250000)
        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:100,000"), 100000)
        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:50,000"), 50000)
        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:25,000"), 25000)
        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:10,000"), 10000)
        return self.setting_widget

    def add_basemap_to_qgis(self):
        """add the selected grid to qgis central canvas."""
        selected_items = self.setting_form.listWidget.selectedItems()
        if len(selected_items) == 0:
            return False

        selected_grid_mesh_name = selected_items[0].text()
        if selected_grid_mesh_name == "经纬网":
            self.build_lon_lat_grid()
        return True

    def unload(self):
        pass

    def handle_listwidget_item_clicked(self, item : QListWidgetItem):
        if item.text() == "接图表":
            self.setting_form.stackedWidget.setCurrentIndex(0)
        elif item.text() == "经纬网":
            self.setting_form.stackedWidget.setCurrentIndex(1)
        elif item.text() == "方里网":
            self.setting_form.stackedWidget.setCurrentIndex(2)
        elif item.text() == "重要纬线":
            self.setting_form.stackedWidget.setCurrentIndex(3)

    def build_lon_lat_grid(self) -> bool:
        lon_interval = float(self.setting_form.lineEditLonInterval.text())
        lat_interval = float(self.setting_form.lineEditLatInterval.text())
        if lon_interval == 0:
            QMessageBox.warning(self.setting_widget, GlobalHelper.tr( "Warning"), GlobalHelper.tr( "Please enter a valid longitude interval."),QMessageBox.Ok)
            return False
        if lat_interval == 0:
            QMessageBox.warning(self.setting_widget, GlobalHelper.tr( "Warning"), GlobalHelper.tr( "Please enter a valid latitude interval."),QMessageBox.Ok)
            return False

        layer = self.__create_vector_layer(GlobalHelper.tr("Latitude and Longitude Grid") + f"_{lon_interval}_{lat_interval}")
        layer.startEditing()

        # build longitude line
        lon = -180
        while lon < 180:
            qgspointxy_array = []
            point_top = QgsPointXY(lon, -90)
            point_bottom = QgsPointXY(lon, 90)
            qgspointxy_array.append(point_top)
            qgspointxy_array.append(point_bottom)
            line_geometry = QgsGeometry.fromPolylineXY(qgspointxy_array)

            # build feature
            feature = QgsFeature()
            feature.setGeometry(line_geometry)
            feature.setFields(self.layer_fields)

            # set attribute
            feature.setAttributes(["longitude", lon])

            layer.addFeature(feature)

            lon += lon_interval

        # build latitude line
        lat = -90
        while lat < 90:
            qgspointxy_array = []
            point_top = QgsPointXY(-180, lat)
            point_bottom = QgsPointXY(180, lat)
            qgspointxy_array.append(point_top)
            qgspointxy_array.append(point_bottom)
            line_geometry = QgsGeometry.fromPolylineXY(qgspointxy_array)

            # build feature
            feature = QgsFeature()
            feature.setGeometry(line_geometry)
            feature.setFields(self.layer_fields)

            # set attribute
            feature.setAttributes(["latitude", lat])

            layer.addFeature(feature)

            lat += lat_interval

        layer.commitChanges()
        QgsProject.instance().addMapLayer(layer)
        return True

    def __create_vector_layer(self, layer_name) -> QgsVectorLayer:
        # specific vector parameters.
        geometry_name = "LineString"
        crs_name = "EPSG:4326"

        # create vector layer using memory provider.
        layer = QgsVectorLayer(f"{geometry_name}?crs={crs_name}", layer_name, "memory")
        layer.dataProvider().addAttributes(self.layer_fields)
        layer.updateFields()

        return layer





