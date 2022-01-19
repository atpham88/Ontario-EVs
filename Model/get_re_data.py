import os
import shutil
import glob
import pandas as pd
import re

def renewable_data(data_dir,solar_src_dir,solar_dst_dir,wind_src_dir,wind_dst_dir,hour):

    # Put all solar data into one csv file:
    for root, dirs, files in os.walk(solar_src_dir):
        for f in files:
            if f.endswith('.csv'):
                shutil.copy(os.path.join(root,f), solar_dst_dir)

    cwd = os.path.dirname(solar_dst_dir)
    all_files = glob.glob(solar_dst_dir + "Solar*.csv")

    li = []
    for filename in all_files:
        header_temp = re.search("(.*).csv", filename)
        header = header_temp.group(1)
        header = header[-12: -5]
        df = pd.read_csv(filename, usecols=range(1, 2))
        df = df.rename({'CapacityFactor': header}, axis=1)
        li.append(df)
    frame = pd.concat(li, axis=1)
    li =[frame]
    frame = pd.concat(li, axis=1)
    frame_solar = frame.T
    frame_solar[8753] = frame_solar[8752] * 0
    frame_solar[8754] = frame_solar[8752] * 0
    frame_solar[8755] = frame_solar[8752] * 0
    frame_solar[8756] = frame_solar[8752] * 0
    frame_solar[8757] = frame_solar[8752] * 0
    frame_solar[8758] = frame_solar[8752] * 0
    frame_solar[8759] = frame_solar[8752] * 0

    frame_solar['merra_loc'] = frame_solar.index
    frame_solar['latitude_MERRA'] = frame_solar['merra_loc'].str.slice(0, 3)
    frame_solar['longitude_MERRA'] = frame_solar['merra_loc'].str.slice(4, 7)
    frame_solar['plant ID'] = 'Solar'
    frame_solar['latitude_MERRA'] = frame_solar['latitude_MERRA'].astype(float)
    frame_solar['longitude_MERRA'] = frame_solar['longitude_MERRA'].astype(float)

    # Put all wind data into one csv file:
    for root, dirs, files in os.walk(wind_src_dir):
        for f in files:
            if f.endswith('.csv'):
                shutil.copy(os.path.join(root,f), wind_dst_dir)

    cwd = os.path.dirname(wind_dst_dir)
    all_files = glob.glob(wind_dst_dir + "Wind*.csv")

    li = []
    for filename in all_files:
        header_temp = re.search("(.*).csv", filename)
        header = header_temp.group(1)
        header = header[-12: -5]
        df = pd.read_csv(filename, usecols=range(1, 2))
        df = df.rename({'CapacityFactor': header}, axis=1)
        li.append(df)
    frame = pd.concat(li, axis=1)
    li =[frame]
    frame = pd.concat(li, axis=1)
    frame_wind = frame.T

    frame_wind['merra_loc'] = frame_wind.index
    frame_wind['latitude_MERRA'] = frame_wind['merra_loc'].str.slice(0, 3)
    frame_wind['longitude_MERRA'] = frame_wind['merra_loc'].str.slice(4, 7)
    frame_wind['plant ID'] = 'Wind'
    frame_wind['latitude_MERRA'] = frame_wind['latitude_MERRA'].astype(float)
    frame_wind['longitude_MERRA'] = frame_wind['longitude_MERRA'].astype(float)

    # Read in Silver Inputs:
    silver_input = pd.read_excel(data_dir+'SILVER Inputs.xlsx', sheet_name='VRE Plants')

    # Merge solar and wind data with silver:
    solar_data = frame_solar.merge(silver_input,left_on=['plant ID','longitude_MERRA','latitude_MERRA'],
                                   right_on=['plant ID','longitude_MERRA','latitude_MERRA'],how='right')
    solar_data = solar_data[solar_data['plant ID'] == 'Solar']
    solar_data = solar_data.drop(['merra_loc','latitude_MERRA','longitude_MERRA','kind','latitude','longitude',
                     'bus (ignore)','technology type','unit capacity [kW]'], axis=1)
    solar_data_fill = solar_data[solar_data['name'] == 'Solar_5']
    solar_data = solar_data.reset_index()
    solar_data = solar_data.drop(['index'], axis=1)
    solar_data.iloc[11,0:hour] = solar_data_fill.iloc[0,0:hour]

    wind_data = frame_wind.merge(silver_input, left_on=['plant ID', 'longitude_MERRA', 'latitude_MERRA'],
                                   right_on=['plant ID', 'longitude_MERRA', 'latitude_MERRA'], how='right')
    wind_data = wind_data[wind_data['plant ID'] == 'Wind']
    wind_data = wind_data.drop(['merra_loc', 'latitude_MERRA', 'longitude_MERRA', 'kind', 'latitude', 'longitude',
                                  'bus (ignore)', 'technology type', 'unit capacity [kW]'], axis=1)

    for i in list(range(hour)):
        solar_data.iloc[:,i] = solar_data.iloc[:,i] * solar_data['Capacity (MW)']
        wind_data.iloc[:, i] = wind_data.iloc[:, i] * wind_data['Capacity (MW)']

    solar_name = solar_data['name']
    wind_name = wind_data['name']

    solar_data = solar_data.drop(['plant ID','name','Capacity (MW)'], axis=1)
    wind_data = wind_data.drop(['plant ID', 'name', 'Capacity (MW)'], axis=1)

    solar_cap = {(r, c): solar_data.at[r, c] for r in list(range(len(solar_data))) for c in list(range(hour))}
    wind_cap = {(r, c): wind_data.at[r, c] for r in list(range(len(wind_data))) for c in list(range(hour))}

    unit_solar = len(solar_data)
    unit_wind = len(wind_data)

    return solar_cap, wind_cap, solar_name, wind_name, unit_solar,unit_wind

