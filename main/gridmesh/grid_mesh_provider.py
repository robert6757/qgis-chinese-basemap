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
import math

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize, QVariant, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsRectangle, QgsFields, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsCoordinateTransform, QgsCsException
from qgis.gui import QgsProjectionSelectionDialog, QgsMapToolExtent

from ..abstract_basemap_provider import AbstractBasemapProvider
from ..global_helper import GlobalHelper

from .index_grid_generator import IndexGridGenerator

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

        self.distance_grid_crs = None

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
        self.setting_form.toolButtonSelectBoundary.clicked.connect(self.handle_tool_button_select_boundary_clicked)
        self.setting_form.toolButtonCanvasBoundary.clicked.connect(self.handle_tool_button_canvas_boundary_clicked)
        self.setting_form.toolButtonSelectCRS.clicked.connect(self.handle_tool_button_select_crs_clicked)
        self.setting_form.listWidget.itemDoubleClicked.connect(self.handle_item_double_clicked)

        self.select_area_tool = QgsMapToolExtent(self.iface.mapCanvas())
        self.select_area_tool.extentChanged.connect(self.handle_area_tool_capture)

        self.setting_form.listWidget.setIconSize(QSize(160, 160))
        for grid_mesh_name in self.grid_mesh_list:
            icon = QIcon(os.path.join(os.path.dirname(__file__), '../../image/gridmesh/%s.png' % grid_mesh_name))
            self.setting_form.listWidget.addItem(QListWidgetItem(icon, grid_mesh_name))

        # the default is Index Grid(接图表).
        self.setting_form.listWidget.setCurrentRow(0)
        self.setting_form.stackedWidget.setCurrentIndex(0)

        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:1,000,000"), 1000000)
        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:500,000"), 500000)
        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:250,000"), 250000)
        self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:100,000"), 100000)
        # self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:50,000"), 50000)
        # self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:25,000"), 25000)
        # self.setting_form.cbIndexGridScale.addItem(GlobalHelper.tr("1:10,000"), 10000)
        return self.setting_widget

    def add_basemap_to_qgis(self):
        """add the selected grid to qgis central canvas."""
        selected_items = self.setting_form.listWidget.selectedItems()
        if len(selected_items) == 0:
            return False

        build_result = False
        selected_grid_mesh_name = selected_items[0].text()
        if selected_grid_mesh_name == "经纬网":
            build_result = self.build_lon_lat_grid()
        elif selected_grid_mesh_name == "接图表":
            build_result = self.build_map_index_grid()
        elif selected_grid_mesh_name == "方里网":
            build_result = self.build_distance_grid()
        elif selected_grid_mesh_name == "重要纬线":
            build_result = self.build_major_latitude_lines()

        if not build_result:
            return False

        return True

    def unload(self):
        pass

    def handle_listwidget_item_clicked(self, item : QListWidgetItem):
        if item.text() == "接图表":
            self.setting_form.stackedWidget.setCurrentIndex(0)
        elif item.text() == "经纬网":
            self.setting_form.stackedWidget.setCurrentIndex(1)
        elif item.text() == "方里网":
            if QgsProject.instance() is not None:
                # Retrieve the project's CRS
                self.distance_grid_crs = QgsProject.instance().crs()
                self.setting_form.lineEditCRS.setText(self.distance_grid_crs.authid() + " - " + self.distance_grid_crs.description())
            self.setting_form.stackedWidget.setCurrentIndex(2)
        elif item.text() == "重要纬线":
            self.setting_form.stackedWidget.setCurrentIndex(3)

    def handle_item_double_clicked(self, item : QListWidgetItem):
        if self.add_basemap_to_qgis() is False:
            return
        self.setting_widget.parent().parent().close()

    def handle_tool_button_select_boundary_clicked(self):
        map_canvas = self.iface.mapCanvas()
        if not map_canvas:
            return
        map_canvas.setMapTool(self.select_area_tool)
        self.setting_widget.parent().parent().hide()

    def handle_area_tool_capture(self, extent : QgsRectangle):
        self.setting_form.lineEditBoundaryLeft.setText(str(extent.xMinimum()))
        self.setting_form.lineEditBoundaryRight.setText(str(extent.xMaximum()))
        self.setting_form.lineEditBoundaryTop.setText(str(extent.yMaximum()))
        self.setting_form.lineEditBoundaryBottom.setText(str(extent.yMinimum()))

        # unset map tool
        map_canvas = self.iface.mapCanvas()
        map_canvas.unsetMapTool(self.select_area_tool)
        self.setting_widget.parent().parent().show()

    def handle_tool_button_canvas_boundary_clicked(self):
        map_canvas = self.iface.mapCanvas()
        if not map_canvas:
            return
        map_extent = map_canvas.extent()
        self.setting_form.lineEditBoundaryLeft.setText(str(map_extent.xMinimum()))
        self.setting_form.lineEditBoundaryRight.setText(str(map_extent.xMaximum()))
        self.setting_form.lineEditBoundaryTop.setText(str(map_extent.yMaximum()))
        self.setting_form.lineEditBoundaryBottom.setText(str(map_extent.yMinimum()))

    def handle_tool_button_select_crs_clicked(self):
        crs_selector_dlg = QgsProjectionSelectionDialog(self.setting_widget)
        crs_selector_dlg.setCrs(self.distance_grid_crs)
        if crs_selector_dlg.exec():
            self.distance_grid_crs = crs_selector_dlg.crs()

            self.setting_form.lineEditCRS.setText(self.distance_grid_crs.authid() + " - " + self.distance_grid_crs.description())

    def build_lon_lat_grid(self) -> bool:
        lon_interval = float(self.setting_form.lineEditLonInterval.text())
        lat_interval = float(self.setting_form.lineEditLatInterval.text())
        if lon_interval == 0:
            QMessageBox.warning(self.setting_widget, GlobalHelper.tr( "Warning"), GlobalHelper.tr( "Please enter a valid longitude interval."),QMessageBox.Ok)
            return False
        if lat_interval == 0:
            QMessageBox.warning(self.setting_widget, GlobalHelper.tr( "Warning"), GlobalHelper.tr( "Please enter a valid latitude interval."),QMessageBox.Ok)
            return False

        layer_fields = QgsFields()
        layer_fields.append(QgsField("type", QVariant.String))
        layer_fields.append(QgsField("value", QVariant.Double))

        layer = self.__create_vector_layer(GlobalHelper.tr("Latitude and Longitude Grid") + f"_{lon_interval}_{lat_interval}", "LineString", layer_fields)
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
            feature.setFields(layer_fields)

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
            feature.setFields(layer_fields)

            # set attribute
            feature.setAttributes(["latitude", lat])

            layer.addFeature(feature)

            lat += lat_interval

        layer.commitChanges()
        QgsProject.instance().addMapLayer(layer)
        return True

    def build_map_index_grid(self) -> bool:
        scale = self.setting_form.cbIndexGridScale.currentData()

        layer_fields = QgsFields()
        layer_fields.append(QgsField("value", QVariant.String))

        layer = self.__create_vector_layer(GlobalHelper.tr("Map Index Grid") + f"_{scale}", "Polygon", layer_fields)
        layer.startEditing()

        igg = IndexGridGenerator()
        geometry_array = igg.gen_geometry(scale)
        if len(geometry_array) == 0:
            return False

        for geometry in geometry_array:
            feature = QgsFeature()
            feature.setGeometry(geometry["geometry"])
            feature.setFields(layer_fields)

            # set attribute
            feature.setAttributes([geometry["text"]])

            layer.addFeature(feature)

        layer.commitChanges()
        QgsProject.instance().addMapLayer(layer)
        return True

    def build_distance_grid(self) -> bool:
        if len(self.setting_form.lineEditXInterval.text()) == 0 or float(self.setting_form.lineEditXInterval.text()) <= 0:
            QMessageBox.warning(self.setting_widget, GlobalHelper.tr("Warning"),
                                GlobalHelper.tr("Please enter a valid X interval."), QMessageBox.Ok)
            return False
        if len(self.setting_form.lineEditYInterval.text()) == 0 or float(self.setting_form.lineEditYInterval.text()) <= 0:
            QMessageBox.warning(self.setting_widget, GlobalHelper.tr("Warning"),
                                GlobalHelper.tr("Please enter a valid Y interval."), QMessageBox.Ok)
            return False
        if (len(self.setting_form.lineEditBoundaryLeft.text()) == 0 or
                len(self.setting_form.lineEditBoundaryRight.text()) == 0 or
                len(self.setting_form.lineEditBoundaryTop.text()) == 0 or
                len(self.setting_form.lineEditBoundaryBottom.text()) == 0):
            QMessageBox.warning(self.setting_widget, GlobalHelper.tr("Warning"),
                                GlobalHelper.tr("Please enter a valid extent."), QMessageBox.Ok)
            return False

        # the unit is KM.
        x_interval = float(self.setting_form.lineEditXInterval.text()) * 1000
        y_interval = float(self.setting_form.lineEditYInterval.text()) * 1000

        crs = self.distance_grid_crs
        if crs.isGeographic():
            QMessageBox.warning(self.setting_widget, GlobalHelper.tr("Warning"),
                                GlobalHelper.tr("Please select a projected coordinate systems."), QMessageBox.Ok)
            return False

        current_project_crs = QgsProject.instance().crs()
        coord_trans = QgsCoordinateTransform(
            current_project_crs,
            crs,
            QgsProject.instance()
        )

        try:
            # calculate extent in crs
            left_top = QgsPointXY(float(self.setting_form.lineEditBoundaryLeft.text()),
                                  float(self.setting_form.lineEditBoundaryTop.text()))
            left_top = coord_trans.transform(left_top)
            right_bottom = QgsPointXY(float(self.setting_form.lineEditBoundaryRight.text()),
                                      float(self.setting_form.lineEditBoundaryBottom.text()))
            right_bottom = coord_trans.transform(right_bottom)
        except QgsCsException:
            self.iface.messageBar().pushWarning(
                GlobalHelper.tr(u"Grid Mesh Error"),
                GlobalHelper.tr(u"Fail to transform coordinate to ") + crs.authid()
            )
            return False

        layer_fields = QgsFields()
        layer_fields.append(QgsField("center_x", QVariant.Double))
        layer_fields.append(QgsField("center_y", QVariant.Double))

        layer = self.__create_vector_layer(GlobalHelper.tr("Distance Grid") + f"_{x_interval}_{y_interval}",
                                           "Polygon", fields=layer_fields, crs_name=crs.authid())
        if not layer:
            self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create distance grid layer. CRS:") + crs.toProj())
            return False
        layer.startEditing()

        # Check the boundary validity.
        left = min(left_top.x(), right_bottom.x())
        right = max(left_top.x(), right_bottom.x())
        bottom = min(right_bottom.y(), left_top.y())
        top = max(right_bottom.y(), left_top.y())

        # Calculate the count of rows and the count of columns.
        num_cols = math.ceil((right - left) / x_interval)
        num_rows = math.ceil((top - bottom) / y_interval)

        if num_cols * num_rows > 1000000:
            QMessageBox.warning(self.setting_widget, GlobalHelper.tr("Warning"),
                                GlobalHelper.tr("Cannot generate a layer exceeding 1 million grids"), QMessageBox.Ok)
            return False

        # generate cells.
        for row in range(num_rows):
            for col in range(num_cols):
                # calculate the boundary of cell.
                x_min = left + col * x_interval
                x_max = x_min + x_interval
                y_min = bottom + row * y_interval
                y_max = y_min + y_interval

                rect = QgsRectangle(x_min, y_min, x_max, y_max)
                geometry = QgsGeometry.fromRect(rect)

                # add new feature.
                feature = QgsFeature()
                feature.setGeometry(geometry)

                feature.setFields(layer_fields)

                # set attribute
                center_x = (x_min + x_max) / 2.0
                center_y = (y_min + y_max) / 2.0
                feature.setAttributes([center_x,center_y])

                layer.addFeature(feature)

        layer.commitChanges()
        QgsProject.instance().addMapLayer(layer)
        return True

    def build_major_latitude_lines(self):
        layer_fields = QgsFields()
        layer_fields.append(QgsField("type", QVariant.String))
        layer = self.__create_vector_layer(GlobalHelper.tr("Major Latitude Lines"), "LineString", layer_fields)
        layer.startEditing()

        check_state = self.setting_form.cbEquator.checkState()

        # build latitude line
        if self.setting_form.cbEquator.checkState() == Qt.Checked:
            qgspointxy_array = []
            point_top = QgsPointXY(-180, 0)
            point_bottom = QgsPointXY(180, 0)
            qgspointxy_array.append(point_top)
            qgspointxy_array.append(point_bottom)
            line_geometry = QgsGeometry.fromPolylineXY(qgspointxy_array)

            # build feature
            feature = QgsFeature()
            feature.setGeometry(line_geometry)
            feature.setFields(layer_fields)

            # set attribute
            feature.setAttributes([GlobalHelper.tr("Equator")])
            layer.addFeature(feature)

        if self.setting_form.cbTropicalLines.checkState() == Qt.Checked:
            qgspointxy_array = []
            point_top = QgsPointXY(-180, 23.43)
            point_bottom = QgsPointXY(180, 23.43)
            qgspointxy_array.append(point_top)
            qgspointxy_array.append(point_bottom)

            # build feature
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPolylineXY(qgspointxy_array))
            feature.setFields(layer_fields)

            # set attribute
            feature.setAttributes([GlobalHelper.tr("Tropic of Cancer")])
            layer.addFeature(feature)

            qgspointxy_array = []
            point_top = QgsPointXY(-180, -23.43)
            point_bottom = QgsPointXY(180, -23.43)
            qgspointxy_array.append(point_top)
            qgspointxy_array.append(point_bottom)

            # build feature
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPolylineXY(qgspointxy_array))
            feature.setFields(layer_fields)

            # set attribute
            feature.setAttributes([GlobalHelper.tr("Tropic of Capricorn")])
            layer.addFeature(feature)

        if self.setting_form.cbPolarCircles.checkState() == Qt.Checked:
            qgspointxy_array = []
            point_top = QgsPointXY(-180, 66.56667)
            point_bottom = QgsPointXY(180, 66.56667)
            qgspointxy_array.append(point_top)
            qgspointxy_array.append(point_bottom)

            # build feature
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPolylineXY(qgspointxy_array))
            feature.setFields(layer_fields)

            # set attribute
            feature.setAttributes([GlobalHelper.tr("Arctic Circle")])
            layer.addFeature(feature)

            qgspointxy_array = []
            point_top = QgsPointXY(-180, -66.56667)
            point_bottom = QgsPointXY(180, -66.56667)
            qgspointxy_array.append(point_top)
            qgspointxy_array.append(point_bottom)

            # build feature
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPolylineXY(qgspointxy_array))
            feature.setFields(layer_fields)

            # set attribute
            feature.setAttributes([GlobalHelper.tr("Antarctic Circle")])
            layer.addFeature(feature)

        layer.commitChanges()
        QgsProject.instance().addMapLayer(layer)
        return True

    def __create_vector_layer(self, layer_name, geometry_name, fields, crs_name = 'EPSG:4326') -> QgsVectorLayer:
        # create vector layer using memory provider.
        layer = QgsVectorLayer(f"{geometry_name}?crs={crs_name}", layer_name, "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        return layer
