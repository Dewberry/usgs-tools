# usgs-tools

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

# Desription

__usgs-tools__ is a collection of tools, and Apps for interacting with the USGS API to query and download data for specific USGS gages.

---

## Contents:
R and Python scripts interact with the available USGS services.

* `USGStools`: Source codes and functions called by notebooks. Includes also tools to automatically retrieve streamflow data for select [USGS Stream Gages](https://waterdata.usgs.gov/nwis/rt).

* `StreamStats`: Tools to automate the [USGS StreamStats tool](https://www.usgs.gov/mission-areas/water-resources/science/streamstats-streamflow-statistics-and-spatial-analysis-tools?qt-science_center_objects=0#qt-science_center_objects).

* `USGS_Filter_App`: A web mapping application, called the [USGS Gages Annual Flow Peak Tool](https://github.com/Dewberry/usgs-tools/tree/master/R/USGS_filter_app), that generates a csv of peak streamflow data from NWIS sites located within a modifiable bounding box of a user-supplied NWIS gage.

### Notebooks:

- [__GageExplorer__](https://nbviewer.jupyter.org/github/Dewberry/usgs-tools/blob/master/R/Notebooks/GageExplorer.ipynb): USGS Stage/Discharge Gages Discovery. Download Data using the USGS Data Retrieval.

- [__USGS_gage_filter__](https://nbviewer.jupyter.org/github/Dewberry/usgs-tools/blob/master/R/Notebooks/USGS_gage_filter.ipynb): Filter USGS gages based on the record availability and drainage area similarity for a given USGS station.

- [__ClipRaster_withMask__](https://nbviewer.jupyter.org/github/Dewberry/usgs-tools/blob/ready-to-publish/Python/StreamStats/ClipRaster_withMask.ipynb): Tool to clip a stream grid raster by a catchment polygon.

- [__StreamStats_API_Scraper_Auto__](https://nbviewer.jupyter.org/github/Dewberry/usgs-tools/blob/ready-to-publish/Python/StreamStats/StreamStats_API_Scraper_Auto.ipynb): Tool to automatically run the [USGS StreamStats tool](https://www.usgs.gov/mission-areas/water-resources/science/streamstats-streamflow-statistics-and-spatial-analysis-tools?qt-science_center_objects=0#qt-science_center_objects) for multiple points within a catchment and return the flow frequency curves and subcatchment boundaries.

- [__StreamStats_ID_Points__](https://nbviewer.jupyter.org/github/Dewberry/usgs-tools/blob/ready-to-publish/Python/StreamStats/StreamStats_ID_Points.ipynb): Tool to identify confluence pair points for tributaries of a specific length, add points to the main stem of a stream network at a specific distance interval, and export a shapefile of the points.

- [__R_Notebook_Discharge_and_Precipitation_Calculation__](https://github.com/Dewberry/usgs-tools/blob/r-markdown/R/Notebooks/Region2-Discharge-Precipitation.rmd): Calculates discharge for each FEMA Region II USGS Riverine and Tidal Gauge. Then calculates a cumulative precipitation amount for these USGS River Gauges across various 2000-2018 storm events affecting FEMA Region II (NY, NJ, PR).
---

## References:

[USGS-R](https://github.com/USGS-R)

[dataRetrieval](https://github.com/USGS-R/dataRetrieval)
