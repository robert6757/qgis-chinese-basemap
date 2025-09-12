# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               TencentBasemapProvider
 Implemented class based on Tencent map.

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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt import QtGui
from qgis.PyQt import QtCore
from qgis.core import QgsProject, QgsRasterLayer

from ..abstract_basemap_provider import AbstractBasemapProvider
from ..global_helper import GlobalHelper

class TencentBasemapProvider(AbstractBasemapProvider):

    def __init__(self):
        # add basemap list
        self.basemap_list = [
            "腾讯矢量底图"
        ]
        self.setting_form = None
        self.setting_widget = None
        self.iface = None

    def attach_iface(self, iface):
        self.iface = iface

    def provider_name(self):
        """name of provider is shown on the list widget"""
        return GlobalHelper.tr(u"Tencent Map")

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
            os.path.dirname(__file__), '../../ui/TencentSettingWidget.ui'))
        if generated_class is None or base_class is None:
            return None

        # build Qt widget
        self.setting_widget = base_class()
        self.setting_form = generated_class()
        self.setting_form.setupUi(self.setting_widget)
        self.setting_form.listWidget.itemDoubleClicked.connect(self.handleItemDClicked)

        self.setting_form.listWidget.setIconSize(QtCore.QSize(160, 160))
        for basemap_name in self.basemap_list:
            icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), '../../image/tencent/%s.png' % basemap_name))
            self.setting_form.listWidget.addItem(QtWidgets.QListWidgetItem(icon, basemap_name))
        return self.setting_widget

    def add_basemap_to_qgis(self):
        """add the selected template of basemap to qgis central canvas."""
        selected_basemap_item = self.setting_form.listWidget.currentItem()
        if selected_basemap_item == None:
            return False

        basemap_name = selected_basemap_item.text()
        if basemap_name == "腾讯矢量底图":
            layer = QgsRasterLayer(
                'type=xyz&url=https://rt0.map.gtimg.com/realtimerender?z%3D%7Bz%7D%26x%3D%7Bx%7D%26y%3D%7B-y%7D%26type%3Dvector%26style%3D0&zmax=18&zmin=0',
                                   '腾讯矢量底图', 'wms')
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)

        return True

    def unload(self):
        pass

