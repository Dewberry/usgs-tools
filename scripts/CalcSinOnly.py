
# -*- coding: utf-8 - Python 2.7.11 *-
"""
Description:See v2 notes.

Input(s):
Output(s):

slawler@dewberry.com
Created on Tue Sep 06 16:20:49 2016
"""

import os, sys
from time import sleep
from glob import glob
import numpy as np

#---Load Functions
MODPATH   = r'W:\CCSI\TECH\NYSERDA\InfrastructureVulnerability\Task8\DATA\Sinuosity\FinalScripts'
sys.path.append(MODPATH)
from SinuosityFunctions_NoSlope import *

#---Assign dirs
root = r"W:\CCSI\TECH\NYSERDA\InfrastructureVulnerability\Task8\DATA\Sinuosity"


#----Load Spaital Data Directories
gdbs= glob(os.path.join(root, r"SS_GeoDatabase\archydro\*"))#---Comment after first run.

#----Assign Ouput Paths
output = os.path.join(root,"culvert_txt_files\\SinCalcs.out")
errors = os.path.join(root,"culvert_txt_files\\SinCalcsError.out")

#----Assign Distance Upstream for Sinuosity Calculation
StreamLength = 5280

def compute_dist(x1,x2,y1,y2):
    d = np.sqrt((x2-x1)**2+ (y2-y1)**2)
    return d


for i, g in enumerate(gdbs):                        #----Loop Through each FAC in list of gdbs
    arcnum = g.split('\\')[-1].split('.')[0]        #----Grab FAC hydroID
    points_file = os.path.join(root,"culvert_txt_files\\{}.txt".format(arcnum))
    df_points = pd.read_csv(points_file)            #---Read in Corresponding Intesected Point File
    points = df_points[['BIN','RASTERVALU', 'ArcHydroID','x','y']] # SLice DataFrame
    print arcnum

    with open(output,'a') as f:
        with open(errors,'a') as elog:

            fac = os.path.join(g,'fac')
            flowgrid = FlowAccGrid(fac)

            for j, point in enumerate(points['RASTERVALU']):
                bridge, p , gdb = points['BIN'][j], points['RASTERVALU'][j], points['ArcHydroID'][j]
                x_coord,y_coord = points['x'][j],points['y'][j]
                idx = np.argwhere(flowgrid.array == p)
                print h2, bridge

                if idx.shape == (1L,2L): # Check Flow Accum Value for uniqueness
                    str_len = 0
                    row,col = idx[0][1], idx[0][0]
                    dspair = flowgrid.transform(row,col)
                    print '[FAC Grid # {}] Unique on Test 1'.format(arcnum)

                else:
                    str_len = 0
                    threshold = 50 #feet
                    print 'Total Matching Points to Filter: ', len(idx)
                    for k, ix in enumerate(idx):
                        row,col = idx[k][1], idx[k][0]
                        dspair_test = flowgrid.transform(row,col)
                        x2,x1,y2,y1 =  dspair_test[0], x_coord, dspair_test[1], y_coord
                        d_from_pt = compute_dist(x1,x2,y1,y2)

                        if  d_from_pt <= threshold:
                            dspair = dspair_test
                            print 'Found Match at #  ', k, '========> ', x1,x2,y1,y2, ': Distance = ', round(d_from_pt,1)
                            break

                        elif row == idx[-1][1] and col== idx[-1][0] and d_from_pt > threshold:
                            ds_pair = ('Null')
                            print 'No Match Found, Last attempt at #  ', k, '========> ', x1,x2,y1,y2, ': Distance = ', round(d_from_pt,1)

                        else:
                            ds_pair = ('Null')
                            #print 'Filtering.... # ', k, '========> ', x1,x2,y1,y2, ': Distance = ', d_from_pt
                            continue

                try:
                    idx_list = [dspair]
                    sleep(1)
                    idx_n = MoveUpstream(flowgrid.dataframe(),row,col)
                    str_len += GetDistance(row,col, dspair[0], dspair[1], cellsize)
                    #print "Calculating upstream path...."

                    while str_len < StreamLength:
                         usxy,idx_n, str_len = UpstreamIterator(flowgrid, idx_n, idx_list, str_len)

                    #print "Calculating parameters...."

                    (pt2pt_dist,
                     str_len,
                     sinuosity) = CalculateResults(dspair, usxy, str_len)


                    output_string = str(bridge) +'\t' + str(round(sinuosity,4)) + '\t' + str(dspair)+ \
                                    '\t' +str(usxy) + '\t'+ str(arcnum) + '\n'

                    #print "Writing to File...."
                    f.write(output_string)

                except:
                    print '                                                        ===================>Error!'
                    elog.write(str(bridge)+'\t'+ str(arcnum) + '\t' + "IDX Error" +'\n')

    gdbs.remove(g)
    print "================================================================="
    print "      {} Processed and Complete, Removing from list              ".format(arcnum)
    print "                                                                 "
    print "      Remaining Grids to Process: {}                             ".format(str(len(gdbs)))
