# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               AMapBasemapProvider
 Implemented class based on AMap(GaoDe).

        begin                : 2025-08-19
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
from qgis.PyQt import QtGui
from qgis.PyQt import QtCore
from qgis.core import QgsProject, QgsRasterLayer, QgsHueSaturationFilter

from ..abstract_basemap_provider import AbstractBasemapProvider
from ..global_helper import GlobalHelper

class AMapBasemapProvider(AbstractBasemapProvider):

    def __init__(self):
        # add basemap list
        self.basemap_list = [
            "高德矢量底图",
            "高德矢量底图-无注记",
            "高德影像底图",
            "高德影像底图-无注记",
            "高德矢量底图-深色",
            "高德矢量底图-深色-无注记",
            "高德矢量底图-灰色",
            "高德矢量底图-灰色-无注记",
            "高德矢量底图-黑色",
            "高德矢量底图-黑色-无注记",
            "高德矢量底图-科技蓝",
            "高德矢量底图-科技蓝-无注记",
            "高德矢量底图-高对比度",
            "高德矢量底图-高对比度-无注记",
            "高德矢量底图-凸显",
            "高德矢量底图-凸显-无注记"
        ]
        self.setting_form = None
        self.setting_widget = None
        self.iface = None

    def attach_iface(self, iface):
        self.iface = iface

    def provider_name(self):
        """name of provider is shown on the list widget"""
        return GlobalHelper.tr(u"AMap")

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
            os.path.dirname(__file__), '../../ui/AMapSettingWidget.ui'))
        if generated_class is None or base_class is None:
            return None

        # build Qt widget
        self.setting_widget = base_class()
        self.setting_form = generated_class()
        self.setting_form.setupUi(self.setting_widget)
        self.setting_form.listWidget.itemDoubleClicked.connect(self.handleItemDClicked)

        self.setting_form.listWidget.setIconSize(QtCore.QSize(160, 160))
        for basemap_name in self.basemap_list:
            icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), '../../image/amap/%s.png' % basemap_name))
            self.setting_form.listWidget.addItem(QtWidgets.QListWidgetItem(icon, basemap_name))
        return self.setting_widget

    def add_basemap_to_qgis(self):
        """add the selected template of basemap to qgis central canvas."""
        selected_basemap_item = self.setting_form.listWidget.currentItem()
        if selected_basemap_item is None:
            return False

        basemap_name = selected_basemap_item.text()
        if basemap_name == "高德影像底图":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webst01.is.autonavi.com/appmaptile?style%3D6%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=18&zmin=0',
                                   '高德卫星影像', 'wms')
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)

            layer = QgsRasterLayer(
                'type=xyz&url=https://webst01.is.autonavi.com/appmaptile?style%3D8%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=18&zmin=0',
                '高德卫星影像注记', 'wms')
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德影像底图-无注记":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webst01.is.autonavi.com/appmaptile?style%3D6%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=18&zmin=0',
                                   '高德卫星影像', 'wms')
            if not layer.isValid():
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D1%26style%3D8&zmax=18&zmin=0',
                '高德矢量', 'wms')
            if not layer.isValid():
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-无注记":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D2%26style%3D8&zmax=18&zmin=0',
                '高德矢量-无注记', 'wms')
            if not layer.isValid():
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-凸显":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D1%26style%3D8&zmax=18&zmin=0',
                '高德矢量-凸显', 'wms')
            if not layer.isValid():
                return False
            layer.brightnessFilter().setGamma(0.3)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-凸显-无注记":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D2%26style%3D8&zmax=18&zmin=0',
                '高德矢量-凸显-无注记', 'wms')
            if not layer.isValid():
                return False
            layer.brightnessFilter().setGamma(0.3)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-深色":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D1%26style%3D8&zmax=18&zmin=0',
                '高德矢量-深色', 'wms')
            if not layer.isValid():
                return False
            layer.hueSaturationFilter().setInvertColors(True)
            layer.brightnessFilter().setGamma(0.1)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-深色-无注记":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D2%26style%3D8&zmax=18&zmin=0',
                '高德矢量-深色-无注记', 'wms')
            if not layer.isValid():
                return False
            layer.hueSaturationFilter().setInvertColors(True)
            layer.brightnessFilter().setGamma(0.1)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-科技蓝":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D1%26style%3D8&zmax=18&zmin=0',
                '高德矢量-科技蓝', 'wms')
            if not layer.isValid():
                return False
            layer.hueSaturationFilter().setInvertColors(True)
            layer.hueSaturationFilter().setColorizeOn(True)
            layer.hueSaturationFilter().setColorizeColor(QtGui.QColor(57,143,255))
            layer.brightnessFilter().setGamma(0.15)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-科技蓝-无注记":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D2%26style%3D8&zmax=18&zmin=0',
                '高德矢量-科技蓝-无注记', 'wms')
            if not layer.isValid():
                return False
            layer.hueSaturationFilter().setInvertColors(True)
            layer.hueSaturationFilter().setColorizeOn(True)
            layer.hueSaturationFilter().setColorizeColor(QtGui.QColor(57, 143, 255))
            layer.brightnessFilter().setGamma(0.15)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-灰色":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D1%26style%3D8&zmax=18&zmin=0',
                '高德矢量-灰色', 'wms')
            if not layer.isValid():
                return False
            layer.hueSaturationFilter().setGrayscaleMode(QgsHueSaturationFilter.GrayscaleLightness)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-灰色-无注记":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D2%26style%3D8&zmax=18&zmin=0',
                '高德矢量-灰色-无注记', 'wms')
            if not layer.isValid():
                return False
            layer.hueSaturationFilter().setGrayscaleMode(QgsHueSaturationFilter.GrayscaleLightness)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-黑色":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D1%26style%3D8&zmax=18&zmin=0',
                '高德矢量-黑色', 'wms')
            if not layer.isValid():
                return False
            layer.hueSaturationFilter().setGrayscaleMode(QgsHueSaturationFilter.GrayscaleLightness)
            layer.hueSaturationFilter().setInvertColors(True)
            layer.brightnessFilter().setGamma(0.15)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-黑色-无注记":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D2%26style%3D8&zmax=18&zmin=0',
                '高德矢量-黑色-无注记', 'wms')
            if not layer.isValid():
                return False
            layer.hueSaturationFilter().setGrayscaleMode(QgsHueSaturationFilter.GrayscaleLightness)
            layer.hueSaturationFilter().setInvertColors(True)
            layer.brightnessFilter().setGamma(0.15)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-高对比度":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D1%26style%3D8&zmax=18&zmin=0',
                '高德矢量-高对比度', 'wms')
            if not layer.isValid():
                return False
            layer.brightnessFilter().setGamma(0.3)
            layer.brightnessFilter().setContrast(10)
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "高德矢量底图-高对比度-无注记":
            layer = QgsRasterLayer(
                'type=xyz&url=https://webrd01.is.autonavi.com/appmaptile?x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26lang%3Dzh_cn%26size%3D1%26scl%3D2%26style%3D8&zmax=18&zmin=0',
                '高德矢量-高对比度-无注记', 'wms')
            if not layer.isValid():
                return False
            layer.brightnessFilter().setGamma(0.3)
            layer.brightnessFilter().setContrast(10)
            QgsProject.instance().addMapLayer(layer)

        return True

    def unload(self):
        pass



