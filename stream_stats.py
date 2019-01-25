import json
import requests
import sys

def main(rcode, xlocation, ylocation, crs, stats_group, configs):

    waterhsed_url = 'https://streamstats.usgs.gov/streamstatsservices/watershed.geojson?'
    PercentOverlay_url = 'https://gis.streamstats.usgs.gov/arcgis/rest/services/nss/regions/MapServer/exts/PercentOverlayRESTSOE/PercentOverlay'
    stats_groups_url= f"https://streamstats.usgs.gov/nssservices/statisticgroups/{stats_group}.json?"
    scenarios_url = "https://streamstats.usgs.gov/nssservices/scenarios.json?"
    parameters_url = r'https://streamstats.usgs.gov/streamstatsservices/parameters.json?'
    estimate_url = 'https://streamstats.usgs.gov/nssservices/scenarios/estimate.json?'
    Href_url = f"https://streamstats.usgs.gov/nssservices/statisticgroups/{stats_group}"
    
    
    # Make Watershed Call
    watershed_params = {'rcode':rcode, 'xlocation': xlocation,'ylocation':ylocation, 
          'crs':crs, 'includeparameters':'true', 'includefeatures':'true', 'simplify':'true'}

    r = requests.get(waterhsed_url, watershed_params)
    watershed_data = json.loads(r.content.decode())
    watershed_data.keys()
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
        if 'Peak' in group_name and 'Urban' not in group_name:
            regressionregion_codes.append(group['code'])

    regressionregion_codes
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
    r = requests.get(parameters_url, json.loads(parameters_params))
    pdata = r.json()
    
    for i in range(5):
        try:
            use_codes={}
            for p in pdata['parameters']:
                #print(p['code'], p['value'])
                use_codes[p['code']] = p['value']
                
            estimate_params =  {'region': rcode,'statisticgroups':2,'regressionregions':reg_codes,'configs':2}
            r = requests.get(estimate_url, data =estimate_params)
            estimate = r.json()
            break
        except:
            print(f'Fail on {i}...retrying grab parameters')
            
            
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
            #print(rr['Code'])
            rr_list.append(rr)
            rr['PercentWeight']=rr_weight[reg_code.lower()]

    payload['RegressionRegions'] = rr_list
    
    # Call Peak Flows
    peak_flow_url = f"https://streamstats.usgs.gov/nssservices/scenarios/estimate.json?region={rcode}&statisticgroups={stats_group}&regressionregions={reg_codes}&configs={configs}"
    r = requests.post(peak_flow_url, json=json.loads(json.dumps([payload])))
    return r.json()

if __name__== "__main__":
    main()
    