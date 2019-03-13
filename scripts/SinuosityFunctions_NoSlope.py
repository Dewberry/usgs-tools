# -*- coding: utf-8 - Python 2.7.11 *-
'''All classes, methods & functions created for NYSERDA sinuosity and slope
       calculations.'''

import gdal
from math import sqrt
import pandas as pd
import struct

#=======================================================================CONSTANTS
m2ft, m2mi, ft2mi = 3.28084, 0.000621371, 0.000189394

h1 = "\n===================================================================="
h2 = "\n#-----------------------------------------RESULTS FOR Bridge:"

cellsize = 10
#=======================================================================CLASSES
class FlowAccGrid(object):
    '''FlowAccGrid class designed to read in flow accumulation grids from the NY USGS
       Streamstats geodatabase.

       Documentation & additianl info for gdal found here
       https://pypi.python.org/pypi/GDAL/
       https://pcjericks.github.io/py-gdalogr-cookbook/'''

    def __init__(self,path):
        self.path = path
        self.data = gdal.Open(path)
        self.band = self.data.GetRasterBand(1)
        self.array= self.band.ReadAsArray()

    def dataframe(self):
        '''Returns the flow accumulation grid as a pandas dataframe object'''
        df = pd.DataFrame(self.array)
        return df

    def transform(self,x,y):
        '''Method takes indices from dataframe or array and returns projected coordinates'''
        ul_x, x_dim, x_rotation, ul_y, y_rotation, y_dim = self.data.GetGeoTransform()
        x_coord = x * x_dim + ul_x + (x_dim / 2.)
        y_coord = y * y_dim + ul_y + (y_dim / 2.)
        coords = x_coord, y_coord
        return coords

class DemGrid(object):
    '''DemGrid class designed to read in dem grids from the NY USGS
       Streamstats geodatabase.

       Documentation & additianl info for gdal found here
       https://pypi.python.org/pypi/GDAL/
       https://pcjericks.github.io/py-gdalogr-cookbook/'''

    def __init__(self,path):
        self.path = path
        self.data = gdal.Open(path)
        self.transf = self.data.GetGeoTransform()
        self.band = self.data.GetRasterBand(1)
        self.bandtype = gdal.GetDataTypeName(self.band.DataType)
        self.driver = self.data.GetDriver().LongName
        self.transfInv = gdal.InvGeoTransform(self.transf)

    def getvalue(self,x,y):
        # Get pixel value from grid object, x,y should be in reference coordinate system
        px, py = gdal.ApplyGeoTransform(self.transfInv, x, y)
        structval = self.band.ReadRaster(int(px), int(py), 1,1, buf_type = self.band.DataType)
        fmt = 'f'
        intval = struct.unpack(fmt , structval)
        val = round(intval[0],2)
        return val

#========================================================================FUNCTIONS
def index2coords(row, col, upper_left_x,upper_left_y,x_size,y_size):
    '''Convert Indices to Coordinates. Function implemented as 'transform' method in FlowAccGrid object'''
    x_coord = row * x_size + upper_left_x + (x_size / 2)
    y_coord = col * y_size + upper_left_y + (y_size / 2)
    xypair = x_coord, y_coord
    return xypair

def TrueDistance(coord1,coord2):
    '''Computes point to point distance. Not applicable for long distances where earth shape will
        impact the distance significantly. Function expects coord input units to be meters, with
        m2ft converting output to feet'''
    vect_x = coord2[0] - coord1[0]
    vect_y =  coord2[1] - coord1[1]
    return sqrt(vect_x**2 + vect_y**2)*m2ft

def raster2array(raster):
    '''Convert usgs streamstats raster to array'''
    raster = gdal.Open(raster)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray()
    return array

def MoveUpstream(df, row, col):
    '''Function searches surrounding cells in flow accumulation grid to identify the
        grid cell immediately upstream. Ouput is index pair of upstream cell '''
    bridge_flow = df[row][col]
    surr_cells = dict()

    for i in range(-1,2):
        for j in range(-1,2):

            value = df[row + i][col+j] #Read Value of raster cell
            crit_val = 0.3*bridge_flow

            if value > bridge_flow:
                #print "Downstream Cell = ",value
                continue
            elif value == bridge_flow:
                continue
                #print 'Flow at Bridge is ',value
            else:
                surr_cells[value] = [row + i],[col+j]

            key_to_list = []

            for key in surr_cells:
                key_to_list.append(int(key))

    target =  max(key_to_list)
    #print "Upstream Cell is ",  target  #, 'At indices = ', surr_cells[target]
    return surr_cells[target]

def GetDistance(r,c, p0, p1, cellsize):
    '''Function tests input and output index pairs from MoveUpstream to identify distance
        bewteen cell centroids. For lateral moves cellsize is returned, for diagonal moves
        cellsize * sqrt(2) is returned.'''
    if r != p0 and c==p1:
        distance = cellsize*m2ft

    elif r==p1 and c!= p0:
        distance = cellsize*m2ft

    else:
        distance = cellsize*sqrt(2)*m2ft
    return distance

def UpstreamIterator(flowgrid, idx_n, idx_list,str_len):
    '''Algorithm created to iterate over steps to calculate streamline distance and find the
       uus point of interest (stopping point, defined by distance given in while expression in __main__) '''
    r,c = int(idx_n[0][0]),int(idx_n[1][0])
    idx_n = MoveUpstream(flowgrid.dataframe(),r,c)
    xypair = idx_n[0][0],idx_n[1][0]
    str_len += GetDistance(r,c, xypair[0], xypair[1], cellsize)
    usxy = flowgrid.transform(xypair[0],xypair[1])
    idx_list.append(usxy)
    return usxy, idx_n, str_len


def CalculateResults(dspair,usxy,str_len):
    '''Performs calculations for desired parameters (sinuosity) '''
    pt2pt_dist = TrueDistance(dspair,usxy)
    sinuosity = str_len/pt2pt_dist
    return pt2pt_dist,str_len,sinuosity


