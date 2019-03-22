import os
import sys
import json
import glob
import requests
import numpy as np
import pandas as pd


"""
"""

def SS_scrape(rcode, xlocation, ylocation, crs, status=True):
    """
    A function that extracts the catchment boundary and flow frequency data for a specified xy location using the USGS StreamStats web application.
    """
    assert rcode=='MD' or rcode=='NY' or 'WI', "This tool is not been tested for this state and will fail"


    stats_group=2 #Peak-annual flows
    configs=2 #?

    waterhsed_url = 'https://streamstats.usgs.gov/streamstatsservices/watershed.geojson?'
    PercentOverlay_url = 'https://gis.streamstats.usgs.gov/arcgis/rest/services/nss/regions/MapServer/exts/PercentOverlayRESTSOE/PercentOverlay'
    stats_groups_url= f"https://streamstats.usgs.gov/nssservices/statisticgroups/{stats_group}.json?"
    scenarios_url = "https://streamstats.usgs.gov/nssservices/scenarios.json?"
    parameters_url = r'https://streamstats.usgs.gov/streamstatsservices/parameters.json?'
    estimate_url = 'https://streamstats.usgs.gov/nssservices/scenarios/estimate.json?'
    Href_url = f"https://streamstats.usgs.gov/nssservices/statisticgroups/{stats_group}"
    
    # Make Watershed Call
    watershed_params = {'rcode':rcode, 'xlocation': xlocation,'ylocation':ylocation, 'crs':crs, 'includeparameters':'true', 'includefeatures':'true', 'simplify':'true'}
    
    try:
        r = requests.get(waterhsed_url, watershed_params)
        watershed_data = json.loads(r.content.decode())
        if watershed_data['featurecollection'][1]['feature']['features']==[]:
            raise KeyboardInterrupt
    except:
        print("Line 28: Expecting value: line 1 column 1 (char 0")
        count=1
        while watershed_data['featurecollection'][1]['feature']['features']==[]: #This while statement is used to address the issue where the catchment is not succesfully delineated by StreamStats
            print("while loop: watershed_data count:", count)
            r = requests.get(waterhsed_url, watershed_params)
            watershed_data = json.loads(r.content.decode())
            count+=1

    workspaceID = watershed_data['workspaceID']
    featurecollection = watershed_data['featurecollection']
    watershed_poly = featurecollection[1]['feature']
    
    # Make Percent Overlay Call
    PercentOverlay_params = {'geometry': json.dumps(watershed_poly), 'f': 'json'}
    r = requests.post(PercentOverlay_url, PercentOverlay_params)
    PercentOverlay = r.json()
    regressionregion_codes = []
    for group in PercentOverlay:
        group_name = group['name']
        if rcode=='MD':
            if 'Peak' in group_name and 'Urban' not in group_name:
                regressionregion_codes.append(group['code'])
        elif rcode=='NY': 
            if '2006_Full_Region' in group_name: #This has only been tested for region 1 in NY and may need to be adjusted for other regions
                regressionregion_codes.append(group['code'])
        elif rcode=='WI':
        	continue #Flow frequency data is not currently available for Wisconsin so continue to delineating
    reg_codes = ','.join(regressionregion_codes)
    rr_weight={}
    for rr in  PercentOverlay:
        rr_code = rr['code'] 
        if rr_code in regressionregion_codes:
            rr_weight[rr_code] = rr['percent']
            
    # Make Stats groups Call
    stats_groups_url_params = {'region':rcode,'regressionregions':reg_codes}
    r = requests.get(stats_groups_url, json=stats_groups_url_params)
    stats_groups = r.json() 
    
    # Make Scearios Call
    scenarios_url_params = {'region': rcode ,'statisticgroups': stats_group, 'regressionregions':reg_codes, 'configs': 2}
    r = requests.get(scenarios_url, data=scenarios_url_params)
    scenarios = r.json()
    
    rr_parameter_codes=[]
    for rr in scenarios[0]['RegressionRegions']:
        reg_code = rr['Code']
        if reg_code.lower() in reg_codes:
            parameters = rr['Parameters']
            for pp in parameters:
                for k,v in pp.items():
                    if k == 'Code':
                        rr_parameter_codes.append(v)

    rr_parameter_codes = ','.join(list(set(rr_parameter_codes)))
    
    # Make Parameters Call
    parameters_params = json.dumps({'rcode': rcode, 'workspaceID':workspaceID, 'includeparameters': rr_parameter_codes})

    check=1
    while check==1:
        r = requests.get(parameters_url, json.loads(parameters_params))

        while str(r)=='<Response [500]>': #This is to address the issue with getting the parameters...seems to fail every other time. Response [500] means that it has failed, while Response [200] means it was sucesful
            r = requests.get(parameters_url, json.loads(parameters_params))

        pdata = r.json()

        use_codes={}
    
        for p in pdata['parameters']:
            try:
                use_codes[p['code']] = p['value']
                check=0
            except KeyError:
                check=1

    estimate_params =  {'region': rcode,'statisticgroups':2,'regressionregions':reg_codes,'configs':2}

    r = requests.get(estimate_url, data =estimate_params)
              
    est = json.loads(r.content.decode())
    for regregion in est[0]['RegressionRegions']:
        for p in regregion['Parameters']:
            if p['Code'] in use_codes.keys():
                p['Value'] = use_codes[p['Code']]

    # Create Payload
    payload = dict()
    payload["Links"] = [{"rel": "self",
            "Href": Href_url,
            "method": "GET"}] 
    for k, v in stats_groups.items():
        payload[k] = v
    
    payload['StatisticGroupID'] = stats_group
    
    rr_list=[]
    for rr in est[0]['RegressionRegions']:
        reg_code = rr['Code']
        if reg_code.lower() in reg_codes:
            rr_list.append(rr)
            rr['PercentWeight']=rr_weight[reg_code.lower()]

    payload['RegressionRegions'] = rr_list
    
    # Call Peak Flows
    peak_flow_url = f"https://streamstats.usgs.gov/nssservices/scenarios/estimate.json?region={rcode}&statisticgroups={stats_group}&regressionregions={reg_codes}&configs={configs}"
    r = requests.post(peak_flow_url, json=json.loads(json.dumps([payload])))
    if status:
        print('Fetched Peak Flows')
    return watershed_poly, r.json()

  
def get_peaks(ff_json): 
    '''  A function which extracts the flow frequency data from the StreamStats flow frequency json file. 
    Arguments: ff_json is a json file containing the flow frequency data for a catchment outlet
    '''  
    ffdata = {} ##Dictionary to store the outlet flow frequency data dictionaries
    for i in range(len(ff_json[0]['RegressionRegions'][0]['Results'])): #For yeach recurrance interval:
        RI = float(ff_json[0]['RegressionRegions'][0]['Results'][i]['Name'].rstrip('Year Peak Flood')) #Extract the value of the recurrance interval as a float
        Q = ff_json[0]['RegressionRegions'][0]['Results'][i]['Value'] #Extract the corresponding discharge
        ffdata[RI] = Q  #Add the recurrance interval as a key and then the discharge as a value      
    return ffdata

def load_all_results(outputs):
    '''Function to load in all of the results using glob
    '''
    poly_files = glob.glob(os.path.join(outputs,'*.geojson'), recursive = True)
    print('{} Polygon Files Found'.format(len(poly_files)))
    return poly_files
    
def ff_summary(pp_dic):
    """A function to extract the flow frequency data for each outlet within the pp_dic dictionary and create a summary dataframe
    Arguments: pp_dic is a dictionary containing the flow frequency data for each outlet location
    """
    OutID=list(pp_dic.keys()) #The outlet IDs
    ffdata=pd.DataFrame(data={min(OutID):list(pp_dic[min(OutID)].values())},index=list(pp_dic[min(OutID)].keys())) #A dataframe to store the flow frequency data, where the index is the recurrance interval
    ffdata.index.name='RI'#Recurrance interval
    for i in OutID: #Add in the flow frequency data for each catchment outlet
        ffdata[i]=list(pp_dic[i].values()) 
    ffdata = ffdata.reindex(sorted(ffdata.columns), axis=1) #Sort the columns in the dataframe so that the column headers are in increasing order    
    print(ffdata.head())
    return ffdata    