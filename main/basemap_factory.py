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
from .amap.amap_basemap_provider import AMapBasemapProvider
from .tencent.tencent_basemap_provider import TencentBasemapProvider
from .geovisearth.geovisearth_basemap_provider import GeovisEarthBasemapProvider
from .geoviscloud.geoviscloud_basemap_provider import GeovisCloudBasemapProvider
from .jilin1.jilin1_basemap_provider import JiLin1BasemapProvider
from .aliyun.aliyun_basemap_provider import AliyunBasemapProvider

class BaseMapFactory:

    def __init__(self):
        pass

    @staticmethod
    def create_amap_provider(iface):
        bp = AMapBasemapProvider()
        bp.attach_iface(iface)
        return bp

    @staticmethod
    def create_tencent_provider(iface):
        bp = TencentBasemapProvider()
        bp.attach_iface(iface)
        return bp

    @staticmethod
    def create_geovisearth_provider(iface):
        bp = GeovisEarthBasemapProvider()
        bp.attach_iface(iface)
        return bp

    @staticmethod
    def create_geoviscloud_provider(iface):
        bp = GeovisCloudBasemapProvider()
        bp.attach_iface(iface)
        return bp

    @staticmethod
    def create_jilin1_provider(iface):
        bp = JiLin1BasemapProvider()
        bp.attach_iface(iface)
        return bp

    @staticmethod
    def create_aliyun_provider(iface):
        bp = AliyunBasemapProvider()
        bp.attach_iface(iface)
        return bp