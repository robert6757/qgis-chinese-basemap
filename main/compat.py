# -*- coding: utf-8 -*-
"""
/***************************************************************************
                                 Qt5/Qt6 compatibility module
    This module provides compatibility handling for both Qt5 and Qt6 versions
  within the QGIS PyQt environment. It detects the Qt major version at runtime
  and provides flags for conditional code execution based on the version.
                              -------------------
        begin                : 2026-03-18
        copyright            : (C) 2026 by phoenix-gis
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

from qgis.PyQt.QtCore import Qt, QT_VERSION_STR
from qgis.PyQt.QtNetwork import QNetworkReply
from qgis.PyQt.QtWidgets import QMessageBox, QHeaderView

QT_MAJOR_VERSION = int(QT_VERSION_STR.split(".")[0])
IS_QT5 = QT_MAJOR_VERSION == 5
IS_QT6 = QT_MAJOR_VERSION == 6

if IS_QT5:
    LeftDockWidgetArea = Qt.LeftDockWidgetArea
    NoError = QNetworkReply.NoError
    QMessageBoxOk = QMessageBox.Ok
    ResizeToContents = QHeaderView.ResizeToContents
    Checked = Qt.Checked

if IS_QT6:
    LeftDockWidgetArea = Qt.DockWidgetArea.LeftDockWidgetArea
    NoError = QNetworkReply.NetworkError.NoError
    QMessageBoxOk = QMessageBox.StandardButton.Ok
    ResizeToContents = QHeaderView.ResizeMode.ResizeToContents
    Checked = Qt.CheckState.Checked