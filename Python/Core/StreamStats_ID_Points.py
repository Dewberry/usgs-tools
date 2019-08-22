from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point


"""
"""


class StreamGrid(object):
    """
    StreamGrid class designed to read in stream grids and create a
    dataframe.
    """
    def __init__(self,path):
        self.path = path
        self.data = gdal.Open(path)
        self.band = self.data.GetRasterBand(1)
        self.array= self.band.ReadAsArray()

        
    def dataframe(self):
        """
        Returns the stream grid as a pandas dataframe object
        """
        df = pd.DataFrame(self.array)
        return df

    
    def crs_value(self):
        """
        Return the coordinate refernce system value (epsg)
        """
        proj=self.crs=osr.SpatialReference(wkt=self.data.GetProjection()) 
        crs=proj.GetAttrValue('AUTHORITY',1) #Extract the projection
        return crs

    
    def cell_size(self):
        """
        Return the cell height/width
        """
        _,pixelwidth,_,_,_,pixelheight=self.data.GetGeoTransform()
        # assert pixelwidth == -pixelheight,
        # "Expecting pixel height and width to be equal"
        return pixelwidth


def coord2index(sg, lat, lon):
    """
    A function to transform the provided latitude and longitude value of a 
    point on the stream grid into the index (row/column) values for the stream
    grid dataframe.
    :param sg:
    :param lat:
    :param lon:
    :return:
    """
    # Get the geotransform parameters
    transform = sg.data.GetGeoTransform()
    # Row value
    pix_x = int((lon - transform[0]) / transform[1])
    # Column value
    pix_y = int((transform[3] - lat ) / -transform[5])
    return pix_x, pix_y


def index2coord(sg, confl):
    """
    :param sg:
    :param confl:
    :return:
    """
    transform = sg.data.GetGeoTransform()
    longitude = []
    latitude = []

    for i in range(len(confl)):
        longitude.append(((transform[1] * confl[i][0]) + transform[0]) +
                         transform[1]/2.)
        latitude.append((transform[3] - (confl[i][1] * -transform[5])) +
                        transform[5]/2.)
    return longitude, latitude


def TrueDistance(cell1, cell2, cellsize):
    """
    Function to calculate the true distance between individual cells
    :param cell1:
    :param cell2:
    :param cellsize:
    :return:
    """
    row = cell1[0] - cell2[0]
    col = cell1[1] - cell2[1]
    dis = np.sqrt(row ** 2 + col ** 2) * cellsize
    return dis 


def geodataframe(longitude, latitude, epsg, cnum = [], distance = [],
                 ttype = []):
    """
    :param longitude:
    :param latitude:
    :param epsg:
    :param cnum:
    :param distance:
    :param ttype:
    :return:
    """
    coord_df=pd.DataFrame(data={'Lon': longitude, 'Lat': latitude})
    coord_df['Coordinates'] = list(zip(coord_df.Lon, coord_df.Lat))
    coord_df['Coordinates'] = coord_df['Coordinates'].apply(Point)
    if len(cnum) > 0:
        coord_df['ID_Num'] = cnum
    if len(distance) > 0:
        coord_df['Distance'] = distance
    if len(ttype) > 0:
        coord_df['type'] = ttype        
    gdf = gpd.GeoDataFrame(coord_df, geometry='Coordinates',
                           crs={'init': 'epsg:%s' %epsg},)
    gdf=gdf.sort_values(by=['ID_Num']) 
    gdf['ID_Num'] = np.arange(0, len(gdf))
    return gdf   


def remove_cnum(next_cell):
    """
    Function to remove the confluence number from the tuple containing
    the row/column number of the stream cell
    :param next_cell:
    :return:
    """
    next_cellwocnum=[]
    for cell in next_cell:
        row = cell[0]
        col = cell[1]
        next_cellwocnum.append((row, col))
    return next_cellwocnum


def MoveUpstream(df: pd.DataFrame, starting_point: tuple, nogo: list,
                 cnum: int=None):
    """
    This function searches the 8 cells surrounding it to determine the
    location of the next stream cell(s).
    stream_cell = the current stream cell that will be used to search for
    the next stream cell
    :param df: the dataframe containing the stream raster data
    :param starting_point:
    :param nogo: list of stream cells that do not want to return as a new
                 stream cell
    :param cnum:
    :return:
    """
    # Empty list to store the stream_cells that are returned
    next_cell = []
    
    row = starting_point[0]  #Extract the raster row 
    col = starting_point[1]  #Extract the raster column
    cell_value = df[row][col]  #Determine the value of the cell
    
    if cnum == None:
        cnum = starting_point[2]

    nogo = remove_cnum(nogo)
    
    assertmsg = "The provided cell in MoveUpstream is not a stream cell"
    assert df[row][col] == 1, assertmsg
        
    # For -1, 0, 1 in the vertical direction (move up and down rows)
    for i in range(-1,2):
        # For -1, 0, 1 in the horizontal direction (move across columns)
        for j in range(-1,2):
            # Read value of raster cell
            value = df[row + i][col+j]
            # if value is zero, no stream in this cell
            if value == 0:
                continue  #loop back
            # if value is 1 and the cell is not in the nogo list, then...
            elif value==1 and (row+i, col+j) not in nogo:
                # Add the new cell or cells to the stream_cell list
                next_cell.append((row + i, col+j, cnum))
                
    return next_cell


def Remove_False_Confluence(save_confluence: list):
    """
    Function to separate out points that do not have a confluence pair
    indicating that they are not a true confluence but just two stream
    cells next to each other.
    :param save_confluence:
    :return:
    """
    # Empty list to store the true confluences, i.e. those that are not
    # just two stream cells next to eachother
    true_confluence = []
    # List to store the extracted confluence numbers
    confl_num = []
    # For each stream cell, add the confluence number to a list
    for cell in save_confluence:
        confl_num.append(cell[2])
    
    # For each stream cell, if there are two or more stream cells with the
    # same confluence number, i.e it is a confluence, add to the
    # true_confluence list.
    for cell in save_confluence:
        if confl_num.count(cell[2]) >= 2:
            true_confluence.append(cell)
    # List of cells that were identified as confluences but do not have
    # tributaries
    false_confluence = list(set(save_confluence)-set(true_confluence))
    
    return true_confluence, false_confluence 


def ID_False_ConfluenceLocs(false_confluence: list, nogo: list):
    """
    Function to identify all the cells in nogo associated with the false
    conflunces
    :param false_confluence:
    :param nogo:
    :return:
    """
    false_cnum = []
    false_points = []

    for cell in false_confluence:
        false_cnum.append(cell[2])

    for cell in nogo:
        if cell[2] in false_cnum:
            false_points.append(cell)
        
    false_points = list(set(false_points) - set(false_confluence))
    
    return false_points 


def Remove_False_From_Orig(false_confluence: list,
                           confluence_pairs_orig: list):
    """
    Function to remove any original confluences that are associated with
    the false confluences
    :param false_confluence:
    :param confluence_pairs_orig:
    :return:
    """
    false_cnum = []
    confluence_pairs = []

    for cell in false_confluence:
        false_cnum.append(cell[2])

    for cell in confluence_pairs_orig:
        if cell[2] not in false_cnum:
            confluence_pairs.append(cell)
            
    return confluence_pairs


def Exclude_Confls(tributary: list, disexl: float):
    """
    Function to exclude tributaries or main stem intervals less than the
    exclusion length (disexl)
    :param tributary:
    :param disexl:
    :return:
    """
    incl_tribs = []

    for cell in tributary:
        if cell[3] >= disexl:
            incl_tribs.append(cell)

    return incl_tribs