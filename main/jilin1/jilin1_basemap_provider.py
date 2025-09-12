# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               JiLin1BasemapProvider
 Implemented class based on JiLin-1 cloud.(https://www.jl1mall.com/)

        begin                : 2025-09-12
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
import json

from qgis.PyQt import uic
from qgis.core import QgsProject, QgsRasterLayer, QgsSettings
from qgis.PyQt.QtWidgets import QTableWidgetItem, QMessageBox

from ..abstract_basemap_provider import AbstractBasemapProvider
from ..global_helper import GlobalHelper

class JiLin1BasemapProvider(AbstractBasemapProvider):

    def __init__(self):
        self.setting_form = None
        self.setting_widget = None
        self.iface = None

        self.__qsetting_tag_tk = "qgis-chinese-basemap/jilin1/tk"
        self.__qsetting_tag_mk = "qgis-chinese-basemap/jilin1/mk"

    def attach_iface(self, iface):
        self.iface = iface

    def provider_name(self):
        """name of provider is shown on the list widget"""
        return GlobalHelper.tr(u"JiLin-1")

    def provider_icon(self):
        """icon of provider is shown on the list widget"""
        pass

    def unload(self):
        pass

    def make_setting_widget(self):
        """provide JiLin-1 TK and MK variables."""
        generated_class, base_class = uic.loadUiType(os.path.join(
            os.path.dirname(__file__), '../../ui/JiLin1SettingWidget.ui'))
        if generated_class is None or base_class is None:
            return None

        # build Qt widget
        self.setting_widget = base_class()
        self.setting_form = generated_class()
        self.setting_form.setupUi(self.setting_widget)
        self.setting_form.tableWidget.itemChanged.connect(self.handle_table_item_changed)
        self.setting_form.btnGetToken.clicked.connect(self.handle_get_token_clicked)
        self.setting_form.btnAdd.clicked.connect(self.handle_add_datasource_clicked)
        self.setting_form.btnRemove.clicked.connect(self.handle_remove_datasource_clicked)
        self.setting_form.lineEdit.editingFinished.connect(self.handle_update_tk)

        # initialize UI
        self.setting_form.tableWidget.setColumnCount(2)
        self.setting_form.tableWidget.setColumnWidth(0, 200)
        self.setting_form.tableWidget.setColumnWidth(1, 250)

        # fill widget from QgsSettings
        g_setting = QgsSettings()
        if g_setting.value(self.__qsetting_tag_tk) is not None:
            self.setting_form.lineEdit.setText(g_setting.value(self.__qsetting_tag_tk))

        if g_setting.value(self.__qsetting_tag_mk) is not None:
            mk_json_array = g_setting.value(self.__qsetting_tag_mk)
            self.setting_form.tableWidget.setRowCount(len(mk_json_array))
            for i, mk_json_obj in enumerate(mk_json_array):
                name_table_item = QTableWidgetItem()
                mk_table_item = QTableWidgetItem()
                if "name" in mk_json_obj.keys():
                    name_table_item.setText(mk_json_obj["name"])
                if "mk" in mk_json_obj.keys():
                    mk_table_item.setText(mk_json_obj["mk"])
                self.setting_form.tableWidget.setItem(i, 0, name_table_item)
                self.setting_form.tableWidget.setItem(i, 1, mk_table_item)

        return self.setting_widget

    def add_basemap_to_qgis(self):
        """add the selected data source to qgis central canvas."""
        tk = self.setting_form.lineEdit.text()
        if len(tk) == 0:
            QMessageBox.information(self.setting_widget,
                                    GlobalHelper.tr(u"Tip"),
                                    GlobalHelper.tr(u"Please input your TK."), QMessageBox.Ok)
            return False

        selected_items = self.setting_form.tableWidget.selectedItems()
        if selected_items is None or len(selected_items) == 0:
            QMessageBox.information(self.setting_widget,
                                    GlobalHelper.tr(u"Tip"),
                                    GlobalHelper.tr(u"Please select an imagery from table."), QMessageBox.Ok)
            return False

        row_i = selected_items[0].row()
        name_table_item = self.setting_form.tableWidget.item(row_i, 0)
        if name_table_item is None or len(name_table_item.text()) == 0:
            QMessageBox.information(self.setting_widget,
                                    GlobalHelper.tr(u"Tip"),
                                    GlobalHelper.tr(u"Please input the name of imagery."), QMessageBox.Ok)
            return False

        mk_table_item = self.setting_form.tableWidget.item(row_i, 1)
        if mk_table_item is None or len(mk_table_item.text()) == 0:
            QMessageBox.information(self.setting_widget,
                                    GlobalHelper.tr(u"Tip"),
                                    GlobalHelper.tr(u"Please input the MK of imagery."), QMessageBox.Ok)
            return False

        # add to map canvas
        layer = QgsRasterLayer(
            'type=xyz&url=https://api.jl1mall.com/getMap/%7Bz%7D/%7Bx%7D/%7B-y%7D?mk%3D{1}%26tk%3D{0}&zmax=18&zmin=0'.format(tk, mk_table_item.text()),
            name_table_item.text(), 'wms')
        if not layer.isValid():
            return False
        QgsProject.instance().addMapLayer(layer)
        return True

    def handle_table_item_changed(self, item):
        # self.iface.messageBar().pushMessage("execute handle_item_changed")
        self.__save_mk_tablewidget_to_qgssetting()

    def handle_update_tk(self):
        tk = self.setting_form.lineEdit.text()
        g_setting = QgsSettings()
        g_setting.setValue(self.__qsetting_tag_tk, tk)
        pass

    def handle_add_datasource_clicked(self):
        self.setting_form.tableWidget.setRowCount(self.setting_form.tableWidget.rowCount() + 1)

    def handle_remove_datasource_clicked(self):
        selected_items = self.setting_form.tableWidget.selectedItems()
        if selected_items is None or len(selected_items) == 0:
            return

        row_i = selected_items[0].row()
        self.setting_form.tableWidget.removeRow(row_i)

        self.__save_mk_tablewidget_to_qgssetting()

    def handle_get_token_clicked(self):
        url = "https://www.jl1mall.com/"
        webbrowser.open(url)

    def __save_mk_tablewidget_to_qgssetting(self):
        mk_array = []
        for row_i in range(self.setting_form.tableWidget.rowCount()):
            mk_item = {}
            field_name = self.setting_form.tableWidget.item(row_i, 0)
            if field_name is not None:
                mk_item["name"] = field_name.text()
            field_mk = self.setting_form.tableWidget.item(row_i, 1)
            if field_mk is not None:
                mk_item["mk"] = field_mk.text()
                # ignore empty row
            if len(mk_item.keys()) == 0:
                continue
            mk_array.append(mk_item)

        g_setting = QgsSettings()
        g_setting.setValue(self.__qsetting_tag_mk, mk_array)