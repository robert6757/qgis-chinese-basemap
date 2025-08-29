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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from .basemap_factory import BaseMapFactory

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/AddLayerDlg.ui'))

class AddLayerDlg(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(AddLayerDlg, self).__init__(parent)
        self.setupUi(self)

        # initialize all providers
        self.__provider_pool = {}
        provider_fac = BaseMapFactory()
        # GaoDe Provider
        amap_provider = provider_fac.create_amap_provider(iface)
        self.__provider_pool[amap_provider.provider_name()] = amap_provider
        # Tencent Provider
        tencent_provider = provider_fac.create_tencent_provider(iface)
        self.__provider_pool[tencent_provider.provider_name()] = tencent_provider

        self.__build_list_by_provider_pool()

        self.__setting_widget = None
        self.__selected_provider = None

    def handleClickClose(self):
        self.close()

    def handleClickAdd(self):
        if self.__selected_provider is None:
            return
        self.__selected_provider.add_basemap_to_qgis()
        self.close()

    def handleClickHelp(self):
        pass

    def handleClickDataSource(self, clickedItem):
        # clear previous variable.
        if self.__setting_widget is not None:
            self.settingWidgetLayout.removeWidget(self.__setting_widget)
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

    def __build_list_by_provider_pool(self):
        for provider in self.__provider_pool.values():
            listWidget = self.listDataSource
            listWidget.addItem(provider.provider_name())




