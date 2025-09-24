# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               IndexGridGenerator
 This class generate index grid geometry.

        begin                : 2025-09-19
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

from qgis.core import QgsRectangle, QgsGeometry

class IndexGridGenerator():

    def __init__(self):
        pass

    def gen_geometry(self, scale_denominator: float) -> []:
        geometry_results = []

        if scale_denominator == 1000000:
            factor = 1
        elif scale_denominator == 500000:
            factor = 2
        elif scale_denominator == 250000:
            factor = 4
        elif scale_denominator == 100000:
            factor = 8
        else:
            return geometry_results

        # 3 latitude bands.
        # first band : 0~60° 0~-60°
        letter_tag_band1 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]
        self.process_latitude_band(geometry_results,
                                   0, 60,
                                   6, 4,
                                   -180, 180, factor, letter_tag_band1)
        self.process_latitude_band(geometry_results,
                                   -60, 0,
                                   6, 4,
                                   -180, 180, factor, letter_tag_band1[::-1])

        # second band : 60~76° -60~-76°
        letter_tag_band2 = ["P","Q","R","S"]
        self.process_latitude_band(geometry_results,
                                   60, 76,
                                   12, 4,
                                   -180, 180, factor, letter_tag_band2)
        self.process_latitude_band(geometry_results,
                                   -76, -60,
                                   12, 4,
                                   -180, 180, factor, letter_tag_band2[::-1])

        # third band : 76~88° -76~-88°
        letter_tag_band3 = ["T", "U", "V"]
        self.process_latitude_band(geometry_results,
                                   76, 88,
                                   24, 4,
                                   -180, 180, factor, letter_tag_band3)
        self.process_latitude_band(geometry_results,
                                   -88, -76,
                                   24, 4,
                                   -180, 180, factor, letter_tag_band3[::-1])

        return geometry_results


    def process_latitude_band(self, geometry_results, lat_min, lat_max, lon_interval, lat_interval, boundary_left,
                              boundary_right, factor, letter_tag):
        """Handles the generation of a single latitude band"""
        if lat_min >= lat_max:
            return

        if lat_max > 0:
            direction_name = "N"
        else:
            direction_name = "S"

        # Calculate the starting latitude and ensure it is an integer multiple of the latitude interval.
        start_lat = (int(lat_min / lat_interval) * lat_interval)
        if start_lat < lat_min:
            start_lat += lat_interval

        # Calculate the starting longitude and ensure it is an integer multiple of the longitude interval.
        start_lon = (int(boundary_left / lon_interval) * lon_interval)
        if start_lon < boundary_left:
            start_lon += lon_interval

        # Calculate the longitude and latitude intervals for each small rectangle
        lon_step = lon_interval / factor
        lat_step = lat_interval / factor

        # Generate all grids within this latitude band
        lat_i = start_lat
        lat_index = 0
        while lat_i < lat_max:
            lon_i = start_lon
            lon_index = 0
            while lon_i <= boundary_right:
                # Process the small rectangles within each large rectangle.
                for row in range(factor):
                    for col in range(factor):
                        # Calculate the bounds of the small rectangle
                        small_lon_left = lon_i + col * lon_step
                        small_lat_bottom = lat_i + row * lat_step
                        small_lon_right = small_lon_left + lon_step
                        small_lat_top = small_lat_bottom + lat_step

                        # Create a small rectangular geometric object
                        geometry = QgsGeometry.fromRect(
                            QgsRectangle(small_lon_left, small_lat_bottom, small_lon_right, small_lat_top)
                        )

                        # Generate the code of small rectangles
                        if factor == 1:
                            row_num = ""
                            col_num = ""
                        else:
                            # The encoding rule is from left to right and from top to bottom.
                            row_num = f"{factor-row:03d}"
                            col_num = f"{col+1:03d}"

                        # Add to geometry_result.
                        geometry_result = {
                            "geometry": geometry,
                            "center_lon": small_lon_left + lon_step / 2,
                            "center_lat": small_lat_bottom + lat_step / 2,
                            "text": "{}{}{:02d}{}{}".format(
                                direction_name,
                                letter_tag[lat_index],
                                lon_index + 1,
                                row_num,
                                col_num
                            )
                        }
                        geometry_results.append(geometry_result)

                lon_index += 1
                lon_i += lon_interval
            lat_i += lat_interval
            lat_index += 1

# if __name__ == "__main__":
#     igg = IndexGridGenerator()
#     result = igg.gen_geometry(1000000)
#     pass
