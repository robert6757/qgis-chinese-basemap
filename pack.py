# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ChineseBasemap
                                 Pack plugin script
                              -------------------
        begin                : 2025-08-15
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
import configparser
import zipfile
from pathlib import Path

def main_i():
    current_dir = Path.cwd()
    config = configparser.ConfigParser()
    config.read(current_dir.joinpath("metadata.txt"), encoding="UTF-8")
    version = config.get("general", "version")
    filename = f"qgis-chinese-basemap-{version}.zip"

    # zip the dist directory.
    dist_filepath = current_dir.joinpath("dist")
    dest_zip_filepath = current_dir.joinpath(filename)
    with zipfile.ZipFile(dest_zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in dist_filepath.glob("**/*"):
            zipf.write(file, file.relative_to(dist_filepath.parent))
    print(f"pack finish: {filename}")

if __name__ == "__main__":
    main_i()