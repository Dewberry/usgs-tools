from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

"""
"""


class StreamGrid(object):
    ''' StreamGrid class designed to read in stream grids and create a dataframe.
    '''
    def __init__(self,path):
        self.path = path
        self.data = gdal.Open(path)
        self.band = self.data.GetRasterBand(1)
        self.array= self.band.ReadAsArray()

    def dataframe(self):
        '''Returns the stream grid as a pandas dataframe object
        '''
        df = pd.DataFrame(self.array)
        return df

    def crs_value(self):
        """ Return the coordinate refernce system value (epsg)
        """
        proj=self.crs=osr.SpatialReference(wkt=self.data.GetProjection()) 
        crs=proj.GetAttrValue('AUTHORITY',1) #Extract the projection
        return crs

    def cell_size(self):
        """ Return the cell height/width
        """
        _,pixelwidth,_,_,_,pixelheight=self.data.GetGeoTransform()
        assert pixelwidth==-pixelheight, "Expecting pixel height and width to be equal"
        return pixelwidth        

def coord2index(sg, lat, lon):
    """ A function to transform the provided latitude and longitude value of a 
        point on the stream grid into the index (row/column) values for the stream
        grid dataframe.
    """
    transform=sg.data.GetGeoTransform() #Get the geotransform parameters
    pix_x = int((lon - transform[0]) / transform[1]) #Row value
    pix_y = int((transform[3] - lat ) / -transform[5]) #Column value
    return pix_x, pix_y

def index2coord(sg, confl):
    """
    """
    transform=sg.data.GetGeoTransform()
    longitude=[]
    latitude=[]

    for i in range(len(confl)):
        longitude.append(((transform[1]*confl[i][0])+transform[0])+transform[1]/2.)
        latitude.append((transform[3]-(confl[i][1]*-transform[5]))+transform[5]/2.)
    return longitude, latitude

def TrueDistance(cell1, cell2, cellsize):
    """ Function to calculate the true distance between individual cells
    """
    row=cell1[0]-cell2[0]
    col=cell1[1]-cell2[1]
    dis=np.sqrt(row**2+col**2)*cellsize
    return dis 

def geodataframe(longitude, latitude, epsg, distance=[], cnum=[]):
    """
    """
    coord_df=pd.DataFrame(data={'Lon':longitude,'Lat':latitude})
    coord_df['Coordinates'] = list(zip(coord_df.Lon, coord_df.Lat))
    coord_df['Coordinates'] = coord_df['Coordinates'].apply(Point)
    if len(distance)>0:
        coord_df['Distance'] = distance
    if len(cnum)>0:
    	coord_df['num'] = cnum
    gdf = gpd.GeoDataFrame(coord_df, geometry='Coordinates', crs={'init': 'epsg:%s' %epsg},)
    return gdf   

def remove_cnum(next_cell):
    """Function to remove the confluence number from the tuple containing the row/column number of the stream cell
    """
    next_cellwocnum=[]
    for cell in next_cell:
        row=cell[0]
        col=cell[1]
        next_cellwocnum.append((row,col))
    return next_cellwocnum            

def MoveUpstream(df: pd.DataFrame, starting_point: tuple, nogo: list, cnum: int=None):
    """This function searches the 8 cells surrounding it to determine the location of the next stream cell(s).
        Arguments: df=the dataframe containing the stream raster data, stream_cell=the current stream cell that will be used to search for the next stream cell,
        nogo=list of stream cells that do not want to return as a new stream cell
    """
    next_cell=[] #Empty list to store the stream_cells that are returned
    
    row=starting_point[0] #Extract the raster row 
    col=starting_point[1] #Extract the raster column
    cell_value= df[row][col] #Determine the value of the cell
    
    if cnum==None:
    	cnum=starting_point[2]

    nogo=remove_cnum(nogo)

    assert df[row][col] == 1, "The provided cell in MoveUpstream is not a stream cell"
        
    for i in range(-1,2): #For -1, 0, 1 in the vertical direction (move up and down rows)
        for j in range(-1,2): #For -1, 0, 1 in the horizontal direction (move across columns)
            value = df[row + i][col+j] #Read value of raster cell
            if value == 0: # if value is zero, no stream in this cell
                continue #loop back
            elif value==1 and (row+i, col+j) not in nogo: # if value is 1 and the cell is not in the nogo list, then...
                next_cell.append((row + i, col+j, cnum)) #Add the new cell or cells to the stream_cell list
                
    return next_cell

def Remove_False_Confluence(save_confluence: list):
    """ Function to separate out points that do not have a confluence pair indicating 
        that they are not a true confluence but just two stream cells next to each other. 
    """
    true_confluence=[] #Empty list to store the true confluences, i.e. those that are not just two stream cells next to eachother
    confl_num=[] #List to store the extracted confluence numbers

    for cell in save_confluence: #For each stream cell, add the confluence number to a list
        confl_num.append(cell[2])

    for cell in save_confluence: #For each stream cell, if there are two or more stream cells with the same confluence number, i.e it is a confluence, add to the true_confluence list.
        if confl_num.count(cell[2])>=2:
            true_confluence.append(cell)
        
    false_confluence=list(set(save_confluence)-set(true_confluence)) #List of cells that were identified as confluences but do not have tributaries
    
    return true_confluence, false_confluence 

def ID_False_ConfluenceLocs(false_confluence: list, nogo: list):
    """ Function to identify the original two or more stream cells that were falsely identified as being a confluence.
    """
    false_cnum=[]
    false_points=[]

    for cell in false_confluence:
        false_cnum.append(cell[2])

    for cell in nogo:
        if cell[2] in false_cnum:
            false_points.append(cell)
        
    false_points=list(set(false_points)-set(false_confluence))
    
    return false_points               