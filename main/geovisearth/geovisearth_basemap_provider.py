# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               GeovisEarthBasemapProvider
 Implemented class based on Geovis Earth(https://www.geovisearth.com/).

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

from ..abstract_basemap_provider import AbstractBasemapProvider
from ..global_helper import GlobalHelper

class GeovisEarthBasemapProvider(AbstractBasemapProvider):

    def __init__(self):
        # add basemap list
        self.basemap_list = [
            "星图地球-影像图",
            "星图地球-影像注记",
            "星图地球-2022历史影像",
            "星图地球-2021历史影像",
            "星图地球-矢量地图",
            "星图地球-地形晕渲图",
            "星图地球-地形注记",
            "星图地球-高程图",
            "土地利用China-50m",
            "世界土壤",
            "中国地区植被指数"
        ]
        self.setting_form = None
        self.setting_widget = None
        self.iface = None

        self.__token_tag = "qgis-chinese-basemap/geovis/token"

    def attach_iface(self, iface):
        self.iface = iface

    def provider_name(self):
        """name of provider is shown on the list widget"""
        return "星图地球"

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
            os.path.dirname(__file__), '../../ui/GeovisEarthSettingWidget.ui'))
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
            icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), '../../image/geovisearth/%s.png' % basemap_name))
            list_item = QtWidgets.QListWidgetItem(icon, basemap_name)
            if basemap_name == "世界土壤":
                list_item.setToolTip(GlobalHelper.tr("GlobalHelper", u"referenced by HWSD database."))
            elif basemap_name == "中国地区植被指数":
                list_item.setToolTip(GlobalHelper.tr("GlobalHelper", u"referenced by SPOT-VEGETATION."))
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
        url = None
        if basemap_name == "星图地球-影像图":
            url = ("https://tiles{0}.geovisearth.com/base/v1/img/%7Bz%7D/%7Bx%7D/%7By%7D?format%3Dwebp%26tmsIds%3Dw%26token%3D{1}&zmax=18&zmin=0"
                   .format(random.randint(1,3), token))
        elif basemap_name == "星图地球-影像注记":
            url = ("https://tiles{0}.geovisearth.com/base/v1/cia/%7Bz%7D/%7Bx%7D/%7By%7D?format%3Dwebp%26tmsIds%3Dw%26token%3D{1}&zmax=18&zmin=0"
                .format(random.randint(1, 3), token))
        elif basemap_name == "星图地球-2022历史影像":
            url = ("https://tiles.geovisearth.com/base/v1/2022/img/%7Bz%7D/%7Bx%7D/%7By%7D?format%3Dwebp%26tmsIds%3Dw%26token%3D{0}&zmax=18&zmin=0"
                .format(token))
        elif basemap_name == "星图地球-2021历史影像":
            url = ("https://tiles.geovisearth.com/base/v1/2021/img/%7Bz%7D/%7Bx%7D/%7By%7D?format%3Dwebp%26tmsIds%3Dw%26token%3D{0}&zmax=18&zmin=0"
                .format(token))
        elif basemap_name == "星图地球-矢量地图":
            url = ("https://tiles{0}.geovisearth.com/base/v1/vec/%7Bz%7D/%7Bx%7D/%7By%7D?format%3Dpng%26tmsIds%3Dw%26token%3D{1}&zmax=18&zmin=0"
                   .format(random.randint(1,3), token))
        elif basemap_name == "星图地球-地形晕渲图":
            url = ("https://tiles{0}.geovisearth.com/base/v1/ter/%7Bz%7D/%7Bx%7D/%7By%7D?format%3Dpng%26tmsIds%3Dw%26token%3D{1}&zmax=18&zmin=0"
                   .format(random.randint(1,3), token))
        elif basemap_name == "星图地球-地形注记":
            url = ("https://tiles{0}.geovisearth.com/base/v1/cat/%7Bz%7D/%7Bx%7D/%7By%7D?format%3Dpng%26tmsIds%3Dw%26token%3D{1}&zmax=18&zmin=0"
                   .format(random.randint(1,3), token))
        elif basemap_name == "星图地球-高程图":
            url = ("https://tiles{0}.geovisearth.com/base/v1/terrain-rgb/%7Bz%7D/%7Bx%7D/%7By%7D?format%3Dpng%26tmsIds%3Dw%26token%3D{1}&zmax=18&zmin=0"
                   .format(random.randint(1,3), token))
        elif basemap_name == "土地利用China-50m":
            url = ("https://tiles.geovisearth.com/gxcp/mtsv2/tiles/lu_china/50/1Y/2022/%7Bz%7D/%7Bx%7D/%7By%7D?token%3D{0}&zmax=18&zmin=0"
                   .format(token))
        elif basemap_name == "世界土壤":
            url = ("https://tiles.geovisearth.com/tensphere/v1/water/tiles/hwsd/1000/1Y/1995/%7Bz%7D/%7Bx%7D/%7By%7D?token%3D{0}&zmax=18&zmin=0"
                .format(token))
        elif basemap_name == "中国地区植被指数":
            url = ("https://tiles.geovisearth.com/tensphere/v1/water/tiles/ndv/1000/1D/20080721/%7Bz%7D/%7Bx%7D/%7By%7D?token%3D{0}&zmax=18&zmin=0"
                .format(token))

        if url is None:
            return False

        layer = QgsRasterLayer('type=xyz&url=' + url, basemap_name, 'wms')
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
        return True

    def unload(self):
        pass

    def handleUpdateToken(self):
        token = self.setting_form.lineEdit.text()
        g_setting = QgsSettings()
        g_setting.setValue(self.__token_tag, token)

    def handleGetToken(self):
        url = "https://datacloud.geovisearth.com/"
        webbrowser.open(url)

