# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               TiandituBasemapProvider
 Implemented class based on TianDiTu(天地图).

        begin                : 2025-09-17
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
import webbrowser
import random

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QSize
from qgis.core import QgsProject, QgsRasterLayer, QgsSettings, QgsVectorLayer, QgsLineSymbol, QgsSingleSymbolRenderer, QgsFillSymbol, QgsMarkerSymbol

from ..abstract_basemap_provider import AbstractBasemapProvider
from ..global_helper import GlobalHelper

class TianDiTuProvider(AbstractBasemapProvider):

    def __init__(self):
        # add basemap list
        self.basemap_list = [
            "天地图-矢量底图",
            "天地图-矢量注记",
            "天地图-影像底图",
            "天地图-影像注记",
            "天地图-地形晕渲",
            "天地图-地形注记",
            "天地图-全球境界",
            "天地图-铁路",
            "天地图-公路",
            "天地图-水系线",
            "天地图-水系面",
            "天地图-居民地及设施点",
            "天地图-居民地及设施面",
        ]
        self.setting_form = None
        self.setting_widget = None
        self.iface = None

        self.__token_tag = "qgis-chinese-basemap/tianditu/token"

    def attach_iface(self, iface):
        self.iface = iface

    def provider_name(self):
        """name of provider is shown on the list widget"""
        return GlobalHelper.tr(u"TianDiTu")

    def provider_icon(self):
        """icon of provider is shown on the list widget"""
        pass

    def make_setting_widget(self):
        """provide specific settings and basemap template"""
        generated_class, base_class = uic.loadUiType(os.path.join(
            os.path.dirname(__file__), '../../ui/TianDiTuSettingWidget.ui'))
        if generated_class is None or base_class is None:
            return None

        # build Qt widget
        self.setting_widget = base_class()
        self.setting_form = generated_class()
        self.setting_form.setupUi(self.setting_widget)
        self.setting_form.listWidget.itemDoubleClicked.connect(self.handle_item_double_clicked)
        self.setting_form.btnGetToken.clicked.connect(self.handle_get_token)
        self.setting_form.lineEdit.editingFinished.connect(self.handle_update_token)

        gSetting = QgsSettings()
        token = gSetting.value(self.__token_tag)
        if token is not None:
            self.setting_form.lineEdit.setText(token)

        self.setting_form.listWidget.setIconSize(QSize(160, 160))
        for basemap_name in self.basemap_list:
            icon = QIcon(os.path.join(os.path.dirname(__file__), '../../image/tianditu/%s.png' % basemap_name))
            self.setting_form.listWidget.addItem(QtWidgets.QListWidgetItem(icon, basemap_name))
        return self.setting_widget

    def add_basemap_to_qgis(self):
        """add the selected template of basemap to qgis central canvas."""
        selected_basemap_item = self.setting_form.listWidget.currentItem()
        if selected_basemap_item is None:
            return False

        gSetting = QgsSettings()
        token = gSetting.value(self.__token_tag)
        if token is None or len(token) == 0:
            QtWidgets.QMessageBox.warning(self.setting_widget, GlobalHelper.tr( "Warning"), GlobalHelper.tr( "Please enter a valid access token."),QtWidgets.QMessageBox.Ok)
            return False

        wfs_url = f"http://gisserver.tianditu.gov.cn/TDTService/wfs?tk={token}"

        basemap_name = selected_basemap_item.text()
        if basemap_name == "天地图-矢量底图":
            layer = QgsRasterLayer(
                ('type=xyz&url=https://t{0}.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS%26REQUEST=GetTile%26VERSION=1.0.0%26LAYER=vec%26STYLE=default%26TILEMATRIXSET=w%26FORMAT=tiles%26TileCol=%7Bx%7D%26TileRow=%7By%7D%26TileMatrix=%7Bz%7D%26tk={1}&zmin=1&zmax=18&http-header:referer=https://www.tianditu.gov.cn/'
                 .format(random.randint(0,7), token)), basemap_name, 'wms')
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-矢量注记":
            layer = QgsRasterLayer(
                ('type=xyz&url=https://t{0}.tianditu.gov.cn/cva_w/wmts?SERVICE=WMTS%26REQUEST=GetTile%26VERSION=1.0.0%26LAYER=cva%26STYLE=default%26TILEMATRIXSET=w%26FORMAT=tiles%26TileCol=%7Bx%7D%26TileRow=%7By%7D%26TileMatrix=%7Bz%7D%26tk={1}&zmin=1&zmax=18&http-header:referer=https://www.tianditu.gov.cn/'
                 .format(random.randint(0,7), token)), basemap_name, 'wms')
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-影像底图":
            layer = QgsRasterLayer(
                ('type=xyz&url=https://t{0}.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS%26REQUEST=GetTile%26VERSION=1.0.0%26LAYER=img%26STYLE=default%26TILEMATRIXSET=w%26FORMAT=tiles%26TileCol=%7Bx%7D%26TileRow=%7By%7D%26TileMatrix=%7Bz%7D%26tk={1}&zmin=1&zmax=18&http-header:referer=https://www.tianditu.gov.cn/'
                 .format(random.randint(0,7), token)), basemap_name, 'wms')
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-影像注记":
            layer = QgsRasterLayer(
                ('type=xyz&url=https://t{0}.tianditu.gov.cn/cia_w/wmts?SERVICE=WMTS%26REQUEST=GetTile%26VERSION=1.0.0%26LAYER=cia%26STYLE=default%26TILEMATRIXSET=w%26FORMAT=tiles%26TileCol=%7Bx%7D%26TileRow=%7By%7D%26TileMatrix=%7Bz%7D%26tk={1}&zmin=1&zmax=18&http-header:referer=https://www.tianditu.gov.cn/'
                 .format(random.randint(0,7), token)), basemap_name, 'wms')
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-地形晕渲":
            layer = QgsRasterLayer(
                ('type=xyz&url=https://t{0}.tianditu.gov.cn/ter_w/wmts?SERVICE=WMTS%26REQUEST=GetTile%26VERSION=1.0.0%26LAYER=ter%26STYLE=default%26TILEMATRIXSET=w%26FORMAT=tiles%26TileCol=%7Bx%7D%26TileRow=%7By%7D%26TileMatrix=%7Bz%7D%26tk={1}&zmin=1&zmax=18&http-header:referer=https://www.tianditu.gov.cn/'
                 .format(random.randint(0,7), token)), basemap_name, 'wms')
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-地形注记":
            layer = QgsRasterLayer(
                ('type=xyz&url=https://t{0}.tianditu.gov.cn/cta_w/wmts?SERVICE=WMTS%26REQUEST=GetTile%26VERSION=1.0.0%26LAYER=cta%26STYLE=default%26TILEMATRIXSET=w%26FORMAT=tiles%26TileCol=%7Bx%7D%26TileRow=%7By%7D%26TileMatrix=%7Bz%7D%26tk={1}&zmin=1&zmax=18&http-header:referer=https://www.tianditu.gov.cn/'
                 .format(random.randint(0,7), token)), basemap_name, 'wms')
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-全球境界":
            layer = QgsRasterLayer(
                ('type=xyz&url=https://t{0}.tianditu.gov.cn/ibo_w/wmts?SERVICE=WMTS%26REQUEST=GetTile%26VERSION=1.0.0%26LAYER=ibo%26STYLE=default%26TILEMATRIXSET=w%26FORMAT=tiles%26TileCol=%7Bx%7D%26TileRow=%7By%7D%26TileMatrix=%7Bz%7D%26tk={1}&zmin=1&zmax=18&http-header:referer=https://www.tianditu.gov.cn/'
                 .format(random.randint(0,7), token)), basemap_name, 'wms')
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False
            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-铁路":
            layer_name = "TDTService:LRRL"
            uri = f"url={wfs_url} version='auto' typename='{layer_name}'"
            layer = QgsVectorLayer(uri, basemap_name, "WFS")
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False

            symbol = QgsLineSymbol.createSimple({
                'color': '0,0,0,255',
                'width': '0.5'
            })
            renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(renderer)

            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-公路":
            layer_name = "TDTService:LRDL"
            uri = f"url={wfs_url} version='auto' typename='{layer_name}'"
            layer = QgsVectorLayer(uri, basemap_name, "WFS")
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False

            symbol = QgsLineSymbol.createSimple({
                'color': '254, 205, 120, 255',
                'width': '0.5'
            })
            renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(renderer)

            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-水系线":
            layer_name = "TDTService:HYDL"
            uri = f"url={wfs_url} version='auto' typename='{layer_name}'"
            layer = QgsVectorLayer(uri, basemap_name, "WFS")
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False

            symbol = QgsLineSymbol.createSimple({
                'color': '171, 198, 239, 255',
                'width': '0.5'
            })
            renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(renderer)

            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-水系面":
            layer_name = "TDTService:HYDA"
            uri = f"url={wfs_url} version='auto' typename='{layer_name}'"
            layer = QgsVectorLayer(uri, basemap_name, "WFS")
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False

            symbol = QgsFillSymbol.createSimple({
                'color': '171, 198, 239, 255',
                'outline_color': '0, 0, 0, 0',
                'outline_width': '0'
            })
            renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(renderer)

            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-居民地及设施点":
            layer_name = "TDTService:RESP"
            uri = f"url={wfs_url} version='auto' typename='{layer_name}'"
            layer = QgsVectorLayer(uri, basemap_name, "WFS")
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False

            symbol = QgsMarkerSymbol.createSimple({
                'color': '152, 125, 183, 255',
                'size': '2.5'
            })
            renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(renderer)

            QgsProject.instance().addMapLayer(layer)
        elif basemap_name == "天地图-居民地及设施面":
            layer_name = "TDTService:RESA"
            uri = f"url={wfs_url} version='auto' typename='{layer_name}'"
            layer = QgsVectorLayer(uri, basemap_name, "WFS")
            if not layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} layer from TianDiTu.".format(basemap_name)))
                return False

            symbol = QgsFillSymbol.createSimple({
                'color': '152, 125, 183',
                'outline_color': '0, 0, 0, 255',
                'outline_width': '0.3'
            })
            renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(renderer)

            QgsProject.instance().addMapLayer(layer)

        return True

    def handle_get_token(self):
        url = "https://www.tianditu.gov.cn/"
        webbrowser.open(url)

    def handle_item_double_clicked(self, item):
        if self.add_basemap_to_qgis() is False:
            return
        self.setting_widget.parent().parent().close()

    def handle_update_token(self):
        token = self.setting_form.lineEdit.text()
        g_setting = QgsSettings()
        g_setting.setValue(self.__token_tag, token)

    def unload(self):
        pass



