# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               AbstractBasemapProvider
 Datasource provider base class defining some basic function.

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

from abc import ABC, abstractmethod


class AbstractBasemapProvider(ABC):
    @abstractmethod
    def attach_iface(self, iface):
        """attach qgis python interface."""
        pass

    @abstractmethod
    def provider_name(self):
        """name of provider identified by the provider pool."""
        pass

    @abstractmethod
    def provider_icon(self):
        """icon of provider is shown on the list widget"""
        pass

    @abstractmethod
    def make_setting_widget(self):
        """provider specific settings and basemap template"""
        pass

    @abstractmethod
    def add_basemap_to_qgis(self):
        """add the selected template of basemap to qgis central canvas."""
        pass