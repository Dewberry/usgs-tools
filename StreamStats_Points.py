from osgeo import gdal, ogr, osr
import pandas as pd
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
    row=stream_cell[0][0] #Extract the raster row 
    col=stream_cell[0][1] #Extract the raster column
    cnum=stream_cell[0][2] #Extract the confluence number
    
    cell_value= df[row][col] #Determine the value of the cell
    assert cell_value == 1 #The value of the cell must be equal to the value associated with a stream cell
                 
    nogo.append((row,col)) #Add the row and column as a touple to the nogo list since we do not want to include the current cell in future searches
    stream_cell=[] #Reassign stream_cell as an empty list

    for i in range(-1,2): #For-1, 0, 1 in the vertical direction (move up and down rows)
        for j in range(-1,2): #For -1,0,1 in the horizontal direction (move across columns)
            value = df[row + i][col+j] #Read value of raster cell
            if value == 0: # if value is zero, no stream in this cell
                continue #loop back
            elif value==1 and (row+i,col+j) not in nogo: # if value is 1 and the cell is not in the nogo list, then...
                stream_cell.append((row + i,col+j, cnum+1)) #Add the new cell or cells to the stream_cell list
    return stream_cell, nogo    

def FindConfluence(df, stream_cell, nogo): #Keep moving upstream until you find a confluence--problem: might hit a dead end, maybe add an else if it is the end?
    """Function which repeates the MoveUpstream function until it finds two or more stream cells surrounding the provided stream_cell, indicating a confluence
    """
    while len(stream_cell)==1: #While there is only 1 stream cell returned as we move up stream, keep moving up stream
        stream_cell, nogo=MoveUpstream(df, stream_cell, nogo)
    if len(stream_cell)>1: #If the number of stream cells 
        for i in range(len(stream_cell)):
            nogo.append((stream_cell[i][0],stream_cell[i][1]))
    return stream_cell, nogo

def NextConfluence(df, confl, nogo, ppoints):
    """
    """
    confl1=[]
    stream_cell, nogo=MoveUpstream(df, [confl], nogo) #Move up one cell from the confluence        
    if len(stream_cell)==1:
        stream_cell, nogo=MoveUpstream(df, stream_cell, nogo) #And move up one more time 
        if len(stream_cell)==1:
            ppoints=ppoints+stream_cell #Add the stream_cell that is located three up from the intial split point.
            confl1, nogo=FindConfluence(df, stream_cell, nogo) #Conf1 is empty if end 
        elif len(stream_cell)>1:
            confl1=stream_cell
            for i in range(len(stream_cell)):
                nogo.append((stream_cell[i][0],stream_cell[i][1]))
    elif len(stream_cell)>1:
        confl1=stream_cell
        for i in range(len(stream_cell)):
            nogo.append((stream_cell[i][0],stream_cell[i][1]))
    return confl1, nogo, ppoints   

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

def geodataframe(longitude, latitude, epsg):
    """
    """
    coord_df=pd.DataFrame(data={'Lon':longitude,'Lat':latitude})
    coord_df['Coordinates'] = list(zip(coord_df.Lon, coord_df.Lat))
    coord_df['Coordinates'] = coord_df['Coordinates'].apply(Point)
    gdf = gpd.GeoDataFrame(coord_df, crs={'init': 'epsg:%s' %epsg}, geometry='Coordinates')
    return gdf     