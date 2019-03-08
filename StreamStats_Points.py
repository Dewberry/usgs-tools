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

def MoveUpstream(df, stream_cell, nogo):
    """This function searches the 8 cells surrounding it to determine the location of the next stream cell(s).
        Arguments: df=the dataframe containing the stream raster data, stream_cell=the current stream cell that will be used to search for the next stream cell,
        nogo=list of stream cells that do not want to return as a new stream cell
    """
    row=stream_cell[0] #Extract the raster row 
    col=stream_cell[1] #Extract the raster column
    
    cell_value= df[row][col] #Determine the value of the cell
    assert cell_value == 1 #The value of the cell must be equal to the value associated with a stream cell
    
    nogo.append((row,col))   

    stream_cell=[]
    
    for i in range(-1,2): #For -1, 0, 1 in the vertical direction (move up and down rows)
        for j in range(-1,2): #For -1, 0, 1 in the horizontal direction (move across columns)
            value = df[row + i][col+j] #Read value of raster cell
            if value == 0: # if value is zero, no stream in this cell
                continue #loop back
            elif value==1 and (row+i,col+j) not in nogo: # if value is 1 and the cell is not in the nogo list, then...
                stream_cell.append((row + i,col+j)) #Add the new cell or cells to the stream_cell list
    return stream_cell, nogo    

def FindConfluence(df, stream_cell, nogo): #Keep moving upstream until you find a confluence--problem: might hit a dead end, maybe add an else if it is the end?
    """Function which repeates the MoveUpstream function until it finds two or more stream cells surrounding the provided stream_cell, indicating a confluence
    """
    while len(stream_cell)==1: #While there is only 1 stream cell returned as we move up stream, keep moving up stream
        stream_cell, nogo=MoveUpstream(df, stream_cell[0], nogo)
    if len(stream_cell)>1: #If the number of stream cells 
        nogo=list(set(nogo+stream_cell))
    return stream_cell, nogo

def NextConfluence(df, confl, cellnum, nogo):
    """
    """
    stream_cell, nogo=MoveUpstream(df, confl[cellnum[0]]['pts'][cellnum[1]], nogo) #Move up one cell from the confluence
    if len(stream_cell)==1:
        stream_cell, nogo=MoveUpstream(df, stream_cell[0], nogo) #And move up one more time 
        if len(stream_cell)==1:
            if 'confl' not in confl[cellnum[0]]: #Add the stream_cell that is located three up from the intial split point.
                confl[cellnum[0]]['confl']=stream_cell  
            else:
                confl[cellnum[0]]['confl']=confl[cellnum[0]]['confl']+stream_cell
            stream_cell, nogo=FindConfluence(df, stream_cell, nogo) #Conf1 is empty if end 
            if len(stream_cell)>1:
                confl[max(list(confl.keys()))+1]={'pts':stream_cell, 'npts':len(stream_cell)}
        elif len(stream_cell)>1:
            confl[cellnum[0]]['pts']=confl[cellnum[0]]['pts']+stream_cell
            confl[cellnum[0]]['npts']=len(confl[cellnum[0]]['pts'])
    elif len(stream_cell)>1:
        confl[cellnum[0]]['pts']=confl[cellnum[0]]['pts']+stream_cell
        confl[cellnum[0]]['npts']=len(confl[cellnum[0]]['pts'])
    return confl, nogo    

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

def geodataframe(longitude, latitude, epsg, distance=[]):
    """
    """
    coord_df=pd.DataFrame(data={'Lon':longitude,'Lat':latitude})
    coord_df['Coordinates'] = list(zip(coord_df.Lon, coord_df.Lat))
    coord_df['Coordinates'] = coord_df['Coordinates'].apply(Point)
    if len(distance)>0:
        coord_df['Distance'] = distance
    gdf = gpd.GeoDataFrame(coord_df, geometry='Coordinates', crs={'init': 'epsg:%s' %epsg},)
    return gdf   

def TrueDistance(cell1, cell2, cellsize):
    """ Function to calculate the true distance between individual cells
    """
    row=cell1[0]-cell2[0]
    col=cell1[1]-cell2[1]
    dis=np.sqrt(row**2+col**2)*cellsize
    return dis    