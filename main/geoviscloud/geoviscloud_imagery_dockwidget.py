# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               GeovisCloudImageryDockWidget
 select imagery by different attributes in Geovis Cloud(https://open.geovisearth.com/).

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
import json
import urllib.parse

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem, QMessageBox
from qgis.PyQt.QtCore import QUrl, QUrlQuery
from qgis.PyQt.QtGui import QCloseEvent
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsNetworkAccessManager, QgsRectangle, QgsRasterLayer, QgsPointXY
from qgis.gui import QgsMapToolExtent
from .geoviscloud_selected_area_drawer import SelectedAreaDrawer

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../../ui/GeovisCloudImageryDockWidget.ui'))

class GeovisCloudImageryDockWidget(QDockWidget, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(GeovisCloudImageryDockWidget, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self.network_manager = QgsNetworkAccessManager.instance()
        self.token = None
        self.__params_item_role = 300
        self.__layer_name_item_role = 301

        # initialize UI
        self.history_imagery_root_node = QTreeWidgetItem()
        self.history_imagery_root_node.setText(0, self.tr("History Imagery"))
        self.treeWidget.addTopLevelItem(self.history_imagery_root_node)

        self.sr_imagery_root_node = QTreeWidgetItem()
        self.sr_imagery_root_node.setText(0, self.tr("Super-Resolution Imagery"))
        self.treeWidget.addTopLevelItem(self.sr_imagery_root_node)

        self.btnSelArea.clicked.connect(self.handle_select_area_clicked)
        self.btnClear.clicked.connect(self.handle_clear_clicked)
        self.btnAddToMap.clicked.connect(self.handle_add_to_map)

        self.select_area_tool = QgsMapToolExtent(self.iface.mapCanvas())
        self.select_area_tool.extentChanged.connect(self.handle_area_tool_capture)
        self.selected_area_drawer = None

    def attach_token(self, token):
        self.token = token

    def closeEvent(self, event : QCloseEvent):
        if self.selected_area_drawer is not None:
            self.selected_area_drawer.clear()
        event.accept()

    def handle_select_area_clicked(self):
        canvas = self.iface.mapCanvas()
        if canvas is None:
            return
        canvas.mapTool()
        canvas.setMapTool(self.select_area_tool)

    def handle_clear_clicked(self):
        while self.history_imagery_root_node.childCount() > 0:
            self.history_imagery_root_node.removeChild(self.history_imagery_root_node.child(0))

        while self.sr_imagery_root_node.childCount() > 0:
            self.sr_imagery_root_node.removeChild(self.sr_imagery_root_node.child(0))

        if self.selected_area_drawer is not None:
            self.selected_area_drawer.clear()

        canvas = self.iface.mapCanvas()
        if canvas is not None:
            canvas.refresh()

    def handle_add_to_map(self):
        selected_items = self.treeWidget.selectedItems()
        if len(selected_items) == 0:
            QMessageBox.information(self,
                                    self.tr(u"Tip"),
                                    self.tr(u"Please select the imagery node."), QMessageBox.Ok)
            return

        selected_item = selected_items[0]
        imagery_params = selected_item.data(0, self.__params_item_role)
        layer_name = selected_item.data(0, self.__layer_name_item_role)
        if imagery_params is None or layer_name is None:
            QMessageBox.information(self,
                                    self.tr(u"Tip"),
                                    self.tr(u"Please select the imagery node."), QMessageBox.Ok)
            return

        """
        imagery_params:
        {
            "tiles": [
                "https://api.open.geovisearth.com/v2/getStreamReq/plus/v1/time-series/cities/hefei/hefei_2017/tiles/{z}/{x}/{y}.webp?token=be6db9a4e38fc66641e10c370ebe842fe15304eb411a43417f76652af7e4cafe"
            ],
            "scheme": "xyz",
            "year": "2017",
            "format": "webp",
            "bounds": [
                116.937488,
                31.505384,
                117.74664,
                32.306936
            ],
            "type": "overlay",
            "isIntersect": true
        }
        """
        min_zoom = 0
        max_zoom = 18
        if "minzoom" in imagery_params.keys():
            min_zoom = int(imagery_params["minzoom"])
        if "maxzoom" in imagery_params.keys():
            max_zoom = int(imagery_params["maxzoom"])

        for tile_url in imagery_params["tiles"]:
            endpoint, query_str = tile_url.split("?")

            layer = QgsRasterLayer('type=xyz&url=' + endpoint + "?" + urllib.parse.quote(query_str) + f"&zmin={min_zoom}&zmax={max_zoom}", layer_name, 'wms')
            if not layer.isValid():
                continue
            QgsProject.instance().addMapLayer(layer)

        if "bounds" in imagery_params.keys():
            # move to center of the layer.
            bounds_array = imagery_params["bounds"]
            bound_rect = QgsRectangle(bounds_array[0], bounds_array[1], bounds_array[2], bounds_array[3])

            # Reproject the boundary from the geographic coordinate system to the project's CRS.
            current_project_crs = QgsProject.instance().crs()
            coord_trans = QgsCoordinateTransform(
                QgsCoordinateReferenceSystem("EPSG:4326"),
                current_project_crs,
                QgsProject.instance(),
            )

            layer_bound_in_project_crs = coord_trans.transform(bound_rect)
            canvas = self.iface.mapCanvas()
            if canvas is not None:
                canvas.setExtent(layer_bound_in_project_crs)

    def handle_area_tool_capture(self, extent : QgsRectangle):
        # convert to EPSG:4326
        current_project_crs = QgsProject.instance().crs()
        coord_trans = QgsCoordinateTransform(
            current_project_crs,
            QgsCoordinateReferenceSystem("EPSG:4326"),
            QgsProject.instance(),
        )

        # draw the rect area
        map_canvas = self.iface.mapCanvas()
        if self.selected_area_drawer is None:
            self.selected_area_drawer = SelectedAreaDrawer(map_canvas)

        self.selected_area_drawer.set_area(extent)
        map_canvas.refresh()

        selected_area_extent = coord_trans.transform(extent)
        self.__updpate_history_imagery_node(selected_area_extent)
        self.__updpate_sr_imagery_node(selected_area_extent)

        self.treeWidget.expandAll()

        # unset map tool
        map_canvas.unsetMapTool(self.select_area_tool)

    def __updpate_history_imagery_node(self, extent : QgsRectangle):
        # remove previous children
        while self.history_imagery_root_node.childCount() > 0:
            self.history_imagery_root_node.removeChild(self.history_imagery_root_node.child(0))

        if self.token is None:
            return

        url = QUrl("https://api.open.geovisearth.com/v2/timeSeries/history/city")
        url_query = QUrlQuery()
        url_query.addQueryItem("bbox", '{0},{1},{2},{3}'.format(
            extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()))
        url_query.addQueryItem("token", self.token)
        url.setQuery(url_query)
        request = QNetworkRequest(url)
        reply = self.network_manager.blockingGet(request)
        if reply.error() != QNetworkReply.NoError:
            return
        try:
            reply_json = json.loads(reply.content().data())
        except json.decoder.JSONDecodeError:
            self.iface.messageBar().pushWarning(
                self.tr(u"Geovis Search Error"),
                self.tr(u"Fail to parse results responding from Geovis cloud server.")
            )

        if not self.__check_response_validation(reply_json):
            return

        """
        example of respond:
        {
            "hefei": [
                {
                    "tiles": [
                        "https://api.open.geovisearth.com/v2/getStreamReq/plus/v1/time-series/cities/hefei/hefei_2017/tiles/{z}/{x}/{y}.webp?token=be6db9a4e38fc66641e10c370ebe842fe15304eb411a43417f76652af7e4cafe"
                    ],
                    "scheme": "xyz",
                    "year": "2017",
                    "format": "webp",
                    "bounds": [
                        116.937488,
                        31.505384,
                        117.74664,
                        32.306936
                    ],
                    "type": "overlay",
                    "isIntersect": true
                }
            ]
        }
        """

        # build every region
        for region_name in reply_json.keys():
            region_node = QTreeWidgetItem()
            region_node.setText(0, region_name)

            every_years_params = reply_json[region_name]
            for year_params in every_years_params:
                if "year" not in year_params.keys():
                    continue

                # build year tree node.
                year_str = year_params["year"]
                year_node = QTreeWidgetItem()
                year_node.setText(0, year_str)
                year_node.setData(0, self.__params_item_role, year_params)
                year_node.setData(0, self.__layer_name_item_role, "{0}-{1}".format(region_name, year_str))
                region_node.addChild(year_node)

            self.history_imagery_root_node.addChild(region_node)

    def __updpate_sr_imagery_node(self, extent : QgsRectangle):
        # remove previous children
        while self.sr_imagery_root_node.childCount() > 0:
            self.sr_imagery_root_node.removeChild(self.sr_imagery_root_node.child(0))

        if self.token is None:
            return

        url = QUrl("https://api.open.geovisearth.com/v2/plus/sr/search")
        url_query = QUrlQuery()
        url_query.addQueryItem("bbox", '{0},{1},{2},{3}'.format(
            extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()))
        url_query.addQueryItem("token", self.token)
        url.setQuery(url_query)
        request = QNetworkRequest(url)
        reply = self.network_manager.blockingGet(request)
        if reply.error() != QNetworkReply.NoError:
            return
        try:
            reply_json = json.loads(reply.content().data())
        except json.decoder.JSONDecodeError:
            self.iface.messageBar().pushWarning(
                self.tr(u"Geovis Search Error"),
                self.tr(u"Fail to parse results responding from Geovis cloud server.")
            )

        if not self.__check_response_validation(reply_json):
            return

        """
        example of respond:
        {
            "Anhui_anqing": [
                {
                    "tiles": [
                        "https://api.open.geovisearth.com/v2/getStreamReq/plus/v1/img-sr-all/{z}/{x}/{y}.webp"
                    ],
                    "maxzoom": 18,
                    "format": "webp",
                    "bounds": [
                        116.97900000024993
                        30.49510000006501,
                        117.23030000034476,
                        30.60829999974527
                    ],
                    "minzoom": 18
                }
            ]
        }
        """
        # build every region
        for region_name in reply_json.keys():
            regions = reply_json[region_name]
            for region_i, region_params in enumerate(regions):
                region_node = QTreeWidgetItem()

                if region_i > 0:
                    node_text = region_name + "_{}".format(region_i)
                else:
                    node_text = region_name
                region_node.setText(0, node_text)

                region_node.setData(0, self.__params_item_role, region_params)
                region_node.setData(0, self.__layer_name_item_role, node_text)

                self.sr_imagery_root_node.addChild(region_node)

    def __check_response_validation(self, resp_json) -> bool:
        if type(resp_json) is not dict:
            QMessageBox.warning(self,
                                    self.tr(u"Geovis Response Error"),
                                    self.tr(u"Your request to Geovis cloud server is unavailable."), QMessageBox.Ok)
            return False

        if "code" in resp_json.keys() and resp_json["code"] != 200:
            QMessageBox.warning(self,
                                    self.tr(u"Geovis Response Error"),
                                    self.tr(u"Failed to retrieve data from Geovis cloud. Please check your token's validity and remaining balance"), QMessageBox.Ok)
            return False

        return True



