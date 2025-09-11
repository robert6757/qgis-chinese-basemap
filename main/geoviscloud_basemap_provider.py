# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               GeovisCloudBasemapProvider
 Implemented class based on Geovis Cloud(星图云开放平台 https://open.geovisearth.com/).

        begin                : 2025-08-29
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
import random
import webbrowser

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt import QtGui
from qgis.PyQt import QtCore
from qgis.core import QgsProject, QgsRasterLayer, QgsSettings

from .abstract_basemap_provider import AbstractBasemapProvider
from .global_helper import GlobalHelper
from .geoviscloud_imagery_dockwidget import GeovisCloudImageryDockWidget

class GeovisCloudBasemapProvider(AbstractBasemapProvider):

    def __init__(self):
        # add basemap list
        self.basemap_list = [
            "星图云-影像图",
            "星图云-历史影像",
            "星图云-超分影像",
            "星图云-无水印影像图",
            "星图云-影像注记",
            "星图云-矢量地图",
            "星图云-地形晕渲图",
            "星图云-地形注记",
            "星图云-高程图"
        ]
        self.setting_form = None
        self.setting_widget = None
        self.iface = None

        self.imagery_dockwidget = None

        self.__token_tag = "qgis-chinese-basemap/geoviscloud/token"

    def attach_iface(self, iface):
        self.iface = iface

    def provider_name(self):
        """name of provider is shown on the list widget"""
        return "星图云开放平台"

    def provider_icon(self):
        """icon of provider is shown on the list widget"""
        pass

    def handleItemDClicked(self, item):
        if self.add_basemap_to_qgis() is False:
            return
        self.setting_widget.parent().parent().close()

    def make_setting_widget(self):
        """provide specific settings and basemap template"""
        generated_class, base_class = uic.loadUiType(os.path.join(
            os.path.dirname(__file__), '../ui/GeovisCloudSettingWidget.ui'))
        if generated_class is None or base_class is None:
            return None

        gSetting = QgsSettings()
        token = gSetting.value(self.__token_tag)

        # build Qt widget
        self.setting_widget = base_class()
        self.setting_form = generated_class()
        self.setting_form.setupUi(self.setting_widget)
        self.setting_form.listWidget.itemDoubleClicked.connect(self.handleItemDClicked)
        self.setting_form.lineEdit.editingFinished.connect(self.handleUpdateToken)
        self.setting_form.btnGetToken.clicked.connect(self.handleGetToken)

        if token is not None:
            self.setting_form.lineEdit.setText(token)

        self.setting_form.listWidget.setIconSize(QtCore.QSize(160, 160))
        for basemap_name in self.basemap_list:
            icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), '../image/geoviscloud/%s.png' % basemap_name))
            list_item = QtWidgets.QListWidgetItem(icon, basemap_name)
            self.setting_form.listWidget.addItem(list_item)
        return self.setting_widget

    def add_basemap_to_qgis(self):
        """add the selected template of basemap to qgis central canvas."""
        selected_basemap_item = self.setting_form.listWidget.currentItem()
        if selected_basemap_item is None:
            return False

        gSetting = QgsSettings()
        token = gSetting.value(self.__token_tag)
        if token is None or len(token) == 0:
            QtWidgets.QMessageBox.warning(self.setting_widget, GlobalHelper.tr("GlobalHelper", "Warning"), GlobalHelper.tr("GlobalHelper", "Please enter a valid access token."),QtWidgets.QMessageBox.Ok)
            return False

        basemap_name = selected_basemap_item.text()
        if basemap_name == "星图云-历史影像" or basemap_name == "星图云-超分影像":
            # These imagery requires selection of a specific area on the map, as it does not cover the entire region.
            self.__show_imagery_selector_dockwidget()
            return True

        url = None
        if basemap_name == "星图云-影像图":
            url = ("https://api.open.geovisearth.com/pj/base/v1/img/%7Bz%7D%2F%7Bx%7D%2F%7By%7D?format%3Dwebp%26tmsIds%3Dw%26token%3D{0}&zmax=18&zmin=0"
                   .format(token))
        elif basemap_name == "星图云-影像注记":
            url = ("https://api.open.geovisearth.com/map/v1/cia/%7Bz%7D%2F%7Bx%7D%2F%7By%7D?format%3Dpng%26tmsIds%3Dw%26token%3D{0}&zmax=18&zmin=0"
                   .format(token))
        elif basemap_name == "星图云-矢量地图":
            url = ("https://api.open.geovisearth.com/map/v1/vec/%7Bz%7D/%7Bx%7D/%7By%7D?format%3Dpng%26tmsIds%3Dw%26token%3D{0}&zmax=18&zmin=0"
                   .format(token))
        elif basemap_name == "星图云-地形晕渲图":
            url = ("https://api.open.geovisearth.com/map/v1/ter/%7Bz%7D%2F%7Bx%7D%2F%7By%7D?format%3Dpng%26tmsIds%3Dw%26token%3D{0}&zmax=18&zmin=0"
                   .format(token))
        elif basemap_name == "星图云-地形注记":
            url = ("https://api.open.geovisearth.com/map/v1/cat/%7Bz%7D%2F%7Bx%7D%2F%7By%7D?format%3Dpng%26tmsIds%3Dw%26token%3D{0}&zmax=18&zmin=0"
                   .format(token))
        elif basemap_name == "星图云-高程图":
            url = ("https://api.open.geovisearth.com/map/v1/terrain_rgb/%7Bz%7D%2F%7Bx%7D%2F%7By%7D?format%3Dpng%26tmsIds%3Dw%26token%3D{0}&zmax=18&zmin=0"
                   .format(token))

        if url is None:
            return False

        layer = QgsRasterLayer('type=xyz&url=' + url, basemap_name, 'wms')
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
        return True

    def unload(self):
        if self.imagery_dockwidget is not None:
            self.iface.removeDockWidget(self.imagery_dockwidget)
            self.imagery_dockwidget.close()
            self.imagery_dockwidget = None

    def handleUpdateToken(self):
        token = self.setting_form.lineEdit.text()
        g_setting = QgsSettings()
        g_setting.setValue(self.__token_tag, token)

    def handleGetToken(self):
        url = "https://open.geovisearth.com/"
        webbrowser.open(url)

    def __show_imagery_selector_dockwidget(self):
        if self.imagery_dockwidget is None:
            self.imagery_dockwidget = GeovisCloudImageryDockWidget(self.iface)
            self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.imagery_dockwidget)

        gSetting = QgsSettings()
        token = gSetting.value(self.__token_tag)
        self.imagery_dockwidget.attach_token(token)
        self.imagery_dockwidget.show()
        pass

