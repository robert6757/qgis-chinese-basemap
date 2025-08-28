# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               Basemap factory
 The factory of creating basemap provider.

        begin                : 2025-08-25
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

from .amap_basemap_provider import AMapBasemapProvider

class BaseMapFactory:

    def __init__(self):
        pass

    @staticmethod
    def create_amap_provider(iface):
        bp = AMapBasemapProvider()
        bp.attach_iface(iface)
        return bp