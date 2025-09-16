# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               AliyunBasemapProvider
 Implemented class based on Aliyun(阿里云).

        begin                : 2025-09-16
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
from qgis.PyQt.QtWidgets import QHeaderView, QTreeWidgetItem
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject, QgsVectorLayer

from .region_dictionary import RegionDictionary
from ..abstract_basemap_provider import AbstractBasemapProvider
from ..global_helper import GlobalHelper

class AliyunBasemapProvider(AbstractBasemapProvider):

    def __init__(self):

        self.setting_form = None
        self.setting_widget = None
        self.iface = None

        self.__adcode_item_user_role = 301

    def attach_iface(self, iface):
        self.iface = iface

    def provider_name(self):
        """name of provider is shown on the list widget"""
        return GlobalHelper.tr(u"Aliyun")

    def provider_icon(self):
        """icon of provider is shown on the list widget"""
        pass

    def make_setting_widget(self):
        """provide specific settings and basemap template"""
        generated_class, base_class = uic.loadUiType(os.path.join(
            os.path.dirname(__file__), '../../ui/AliyunSettingWidget.ui'))
        if generated_class is None or base_class is None:
            return None

        # build Qt widget
        self.setting_widget = base_class()
        self.setting_form = generated_class()
        self.setting_form.setupUi(self.setting_widget)

        self.setting_form.lineEdit.textChanged.connect(self.handle_query_key_changed)

        self.init_tree()

        return self.setting_widget

    def add_basemap_to_qgis(self):
        """add the boundary of selected administrative."""
        for selected_item in self.setting_form.treeWidget.selectedItems():
            name = selected_item.text(0)
            adcode = selected_item.data(0, self.__adcode_item_user_role)

            url = "https://geo.datav.aliyun.com/areas_v3/bound/{}.json".format(adcode)
            vector_layer = QgsVectorLayer(url, name, "OGR")
            if not vector_layer.isValid():
                self.iface.messageBar().pushMessage(GlobalHelper.tr("Fail to create {} vectorlayer from Aliyun.".format(name)))
                continue

            QgsProject.instance().addMapLayer(vector_layer)

        return True

    def unload(self):
        pass

    def handle_query_key_changed(self, text : str):
        self.locate_node(text)

    def locate_node(self, name):
        for top_node_i in range(0, self.setting_form.treeWidget.topLevelItemCount()):
            top_node = self.setting_form.treeWidget.topLevelItem(top_node_i)
            if name in top_node.text(0) or name in str(top_node.data(0, self.__adcode_item_user_role)):
                self.setting_form.treeWidget.setCurrentItem(top_node)
                return

            if self.locate_node_i(name, top_node):
                # find node that corresponds with name.
                return

    def locate_node_i(self, name, parent_node) -> bool:
        for child_i in range(0, parent_node.childCount()):
            child_node = parent_node.child(child_i)
            if name in child_node.text(0) or name in str(child_node.data(0, self.__adcode_item_user_role)):
                # select it
                self.setting_form.treeWidget.expandItem(parent_node)
                self.setting_form.treeWidget.setCurrentItem(child_node)
                return True
            if self.locate_node_i(name, child_node):
                return True
        return False

    def init_tree(self):
        self.setting_form.treeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        dic_data = RegionDictionary.get_json()

        self.init_tree_i(dic_data, None)

    def init_tree_i(self, sub_dict_items, parent_item):
        for sub_dict_item in sub_dict_items:
            if parent_item is None:
                parent_item = self.setting_form.treeWidget

            if "市辖区" in sub_dict_item["name"]:
                # Skip nodes with "市辖区" because of a lack of data.
                continue

            # create sub node.
            sub_item = QTreeWidgetItem(parent_item)
            sub_item.setText(0, sub_dict_item["name"])
            sub_item.setData(0, self.__adcode_item_user_role, sub_dict_item["adcode"])

            if "children" in sub_dict_item.keys():
                self.init_tree_i(sub_dict_item["children"], sub_item)
