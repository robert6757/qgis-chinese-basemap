# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               AddLayerDlg
 The main dialog of the plugin which is supporting many datasources for China.

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
import webbrowser

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsApplication

from .basemap_factory import BaseMapFactory

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/AddLayerDlg.ui'))

class AddLayerDlg(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(AddLayerDlg, self).__init__(parent)
        self.setupUi(self)

        self.init_widget_style()

        self.__setting_widget = None
        self.__selected_provider = None

        # initialize all providers
        self.__provider_pool = {}
        provider_fac = BaseMapFactory()
        # GaoDe Provider
        amap_provider = provider_fac.create_amap_provider(iface)
        self.__provider_pool[amap_provider.provider_name()] = amap_provider
        # Tencent Provider
        tencent_provider = provider_fac.create_tencent_provider(iface)
        self.__provider_pool[tencent_provider.provider_name()] = tencent_provider
        # Geovis Earth Provider
        geovis_earth_provider = provider_fac.create_geovisearth_provider(iface)
        self.__provider_pool[geovis_earth_provider.provider_name()] = geovis_earth_provider
        # Geovis Cloud Provider
        geovis_cloud_provider = provider_fac.create_geoviscloud_provider(iface)
        self.__provider_pool[geovis_cloud_provider.provider_name()] = geovis_cloud_provider
        # JiLin-1 Provider
        jilin1_provider = provider_fac.create_jilin1_provider(iface)
        self.__provider_pool[jilin1_provider.provider_name()] = jilin1_provider
        # Aliyun Provider
        aliyun_provider = provider_fac.create_aliyun_provider(iface)
        self.__provider_pool[aliyun_provider.provider_name()] = aliyun_provider
        # TianDiTu Provider
        tianditu_provider = provider_fac.create_tianditu_provider(iface)
        self.__provider_pool[tianditu_provider.provider_name()] = tianditu_provider

        self.__build_list_by_provider_pool()

        # select first provider.
        self.listDataSource.setCurrentRow(0)
        self.handleClickDataSource(self.listDataSource.item(0))

    def init_widget_style(self):

        dlg_style_sheet = """
            QListWidget#listDataSource{
            background-color: rgb(69, 69, 69);
            outline: 0;
            }
            QListWidget#listDataSource::item{
            color: white;
            padding: {0}px;
            }
            QListWidget#listDataSource::item::selected{
            color: palette(window-text);
            background-color:palette(window);
            padding-right: 0px;
            }"""
        dlg_style_sheet = dlg_style_sheet.replace('{0}', str(QgsApplication.scaleIconSize(5)))
        self.setStyleSheet(dlg_style_sheet)

    def handleClickClose(self):
        self.close()

    def handleClickAdd(self):
        if self.__selected_provider is None:
            return
        if self.__selected_provider.add_basemap_to_qgis() is False:
            return
        self.close()

    def handleClickHelp(self):
        url = "https://www.phoenix-gis.cn/d/224-qgischa-jian-shi-yong-wen-ti-hui-zong"
        webbrowser.open(url)

    def handleClickDataSource(self, clickedItem):
        # clear previous variable.
        if self.__setting_widget is not None:
            self.settingWidgetLayout.removeWidget(self.__setting_widget)
            self.__setting_widget.close()
            self.__setting_widget = None
        self.__selected_provider = None

        item_text = clickedItem.text()
        provider = self.__provider_pool[item_text]
        if provider is None:
            return

        # build setting widget
        setting_widget = provider.make_setting_widget()
        self.settingWidgetLayout.addWidget(setting_widget)

        self.__setting_widget = setting_widget
        self.__selected_provider = provider

    def unload(self):
        for key in self.__provider_pool.keys():
            self.__provider_pool[key].unload()

        self.close()

    def __build_list_by_provider_pool(self):
        for provider in self.__provider_pool.values():
            listWidget = self.listDataSource
            listWidget.addItem(provider.provider_name())




