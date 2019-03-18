## Description:
Tools to automate the [USGS StreamStats tool](https://www.usgs.gov/mission-areas/water-resources/science/streamstats-streamflow-statistics-and-spatial-analysis-tools?qt-science_center_objects=0#qt-science_center_objects). The user specifies a stream grid, catchment polygon, catchment outlet, and a desired tributary length. The results of this operation are the flow frequency curves for each tributary confluence and specified main stem location as well as the subcatchment boundaries. 


## Contents:

[ClipRaster_withMask](ClipRaster_withMask.ipynb): Tool to clip a stream grid raster by a catchment polygon.

[StreamStats_ID_Points](StreamStats_ID_Points_v3.ipynb): Tool to identify confluence pair points for tributaries of a specific length, add points to the main stem of a stream network at a specific distance interval, and export a shapefile of the points. 

[StreamStats_API_Scraper_Auto](StreamStats_API_Scraper_Auto.ipynb):	Tool to automatically run the [USGS StreamStats tool](https://www.usgs.gov/mission-areas/water-resources/science/streamstats-streamflow-statistics-and-spatial-analysis-tools?qt-science_center_objects=0#qt-science_center_objects) for multiple points within a catchment and return the flow frequency curves and subcatchment boundaries.

[StreamStats_API_Scraper_debugging](StreamStats_API_Scraper_debugging.ipynb): Working/scrap notebook to debug problems with the [StreamStats_API_Scraper_Auto](StreamStats_API_Scraper_Auto.ipynb) notebook.


## Operation:

##### Run `ClipRaster_withMask.ipynb`:

1. [Download](https://streamstatsags.cr.usgs.gov/StreamGrids/directoryBrowsing.asp) stream grid for the state where the catchment is located. Open and unzip the folder to the desktop. Navigate to the `str900_all` subfolder and open the largest `.adf` file in [QGIS](https://qgis.org/en/site/forusers/download.html). Right click on the layer, highlight `Export`, click `Save As`, set the `Format` to `GeoTIFF`, and specify the location to save the file in `File Name`. Specifically, save this file to the data folder (create if needed) within the same directory as the notebook. 

2. Export the catchment boundary from [QGIS](https://qgis.org/en/site/forusers/download.html) as a GeoJSON. Right click the layer, highlight `Export`, click `Save Feature As`, set the `Format` to `GeoJSON`, and specify the location to save the file in `File Name`.  Make sure this GeoJSON is saved in the same data folder as the stream grid. Note: if the catchment crosses the United State Border into Canada or Mexico, make sure to clip the catchment polygon to include areas in the United States only (StreamStats does not work in Canada). 

3. Open 'ClipRaster_withMask.ipynb' and specify the location of the stream grid, catchment boundary, and where you want to save the clipped stream grid (create a results folder in the same directory as the data folder).

4. Run all cells in the notebook and examine the resulting clipped stream grid raster.

##### Run `StreamStats_ID_Points.ipynb`:

1. Determine the latitude/longitude of the catchment outlet, making sure that the coordinate reference system (crs) is the same as the stream grid raster and that the outlet is overlying the stream grid. Note: the crs for the Maryland stream grid raster is EPSG: 5070, which is not supported by QGIS, so the catchment outlet latitude/longitude needs to be determined using ArcGIS or another compatible GIS software. 

2. Open `StreamStats_ID_Points.ipynb' and specify the path and name of the clipped stream grid raster from `ClipRaster_withMask.ipynb`, the latitude/longitude of the catchment outlet, and the tributary exclusion distance. The tributary exclusion distance is used to exclude confluence pairs whose tributary length is less then the exclusion distance. Note: that if you specify a point other than the catchment outlet, the confluences will still be calculated for the entire stream grid raster.

3. Run all cells in the notebook. The results are saved as a shapefile in the same folder as the clipped stream grid raster.
	
##### Run `StreamStats_API_Scraper_Auto.ipynb`: 

1. Open `StreamStats_API_Scraper_Auto.ipynb`and specify the state abbreviation for the state where the catchment is located and the path of the shapefile containing the latitude and longitude of points on the stream grid from the previous notebook.
 
2. Run all cells in the notebook. The results are saved as a GeoJSON and a CSV file in the results folder within the directory containing this notebook. The GeoJSON file can be opened in [QGIS](https://qgis.org/en/site/forusers/download.html) to examine the catchments that were delineated by the [USGS StreamStats tool](https://www.usgs.gov/mission-areas/water-resources/science/streamstats-streamflow-statistics-and-spatial-analysis-tools?qt-science_center_objects=0#qt-science_center_objects) while the CSV file contains a summary of the flow frequency data for all of the stream points. 

*Author*: sputnam@Dewberry.com
