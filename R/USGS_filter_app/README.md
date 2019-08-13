# USGS Filter App

A web mapping application, called the USGS Gages Annual Flow Peak Tool, that generates a csv of peak streamflow data from NWIS sites located within a modifiable bounding box of a user-supplied NWIS gage.
NWIS stands for the National Water Information System. The NWIS represents the efforts of the United States Geological Survey (USGS) to collect water-resources data at approximately 1.5 million US sites.

## Getting started
To begin using the app, enter a NWIS Site Number in the Site Number input box on the lefthand side of the app, and click Get Site Info.
This will initiate a data retrieval process from the NWIS servers, and present users with the results in the web map on the righthand side.
Summary data will also be presented below the web map. To download peak streamflow data for the selected site, click the Download Data button and save as a CSV file.
While this app can currently only be configured to search by NWIS Site Number, it will soon allow the user to search NWIS sites by Open Street Map geocoded places.

## Features
<!-- --- (Confirm these statements with Mohamed) --- -->
- Default years of Peak Streamflow data are 30. This value sets the bounds for how far back in time peak streamflow data will be retrieved.
- Default Drainage Area Epsilon is 0.25. This value ensures the drainage area of the area of interest across those defined years is between 0.75 X the site's drainage area, and 1.25 X the site's drainage area.
- Default Bounding Box Delta is 1 degree (about 70 miles or 111 km). This value sets the distance conditions for drawing the bounding box around the initial NWIS site.

## Contributing

If you'd like to contribute, please fork the repository and use a feature
branch. Pull requests are warmly welcome.

## Links

- Project homepage: https://github.com/Dewberry/usgs-tools/tree/master/R/USGS_filter_app

## Licensing

The code in this project is licensed under the Apache License 2.0.

<!-- ![Dewberry](https://static1.squarespace.com/static/591216d0197aeaf88cc00895/5934d5d915cf7dc475a10fff/59762a6f59cc6804bf09a4b6/1500916339088/logo-dewberry.png)
![USGS](https://upload.wikimedia.org/wikipedia/commons/0/08/USGS_logo.png) -->
