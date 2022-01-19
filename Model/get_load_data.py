
import pandas as pd
import numpy as np

def load_data(ev_sce, data_dir, day):

    load_data = pd.read_csv(data_dir + 'Ontario Base Demand.csv')
    load_data = load_data[['demand - base (MW)']]
    # EV scenario:
    ev_load_data = pd.read_csv(data_dir + 'EV Charging Scenarios.csv')
    ev_load_data.columns = ev_load_data.iloc[0]
    ev_load_data = ev_load_data.drop(ev_load_data.index[0])
    ev_load_data = ev_load_data.reset_index()
    ev_load_data = ev_load_data.rename(columns={'Home - 1%': 'EV1', 'Home - 5%': 'EV5', 'Home - 10%': 'EV10',
                                                'Home - 20%': 'EV20', 'Home - 30%': 'EV30'})
    ev_load_data = ev_load_data.astype(float)
    ev_load_data = ev_load_data.drop(columns=['index', 'Hour of Day'])
    ev_load_data = pd.concat([ev_load_data] * day, ignore_index=True)

    load_sce = load_data
    load_sce = load_sce.rename(columns={'demand - base (MW)': 'base'})
    load_sce['EV1'] = load_sce['base'] + ev_load_data['EV1']
    load_sce['EV5'] = load_sce['base'] + ev_load_data['EV5']
    load_sce['EV10'] = load_sce['base'] + ev_load_data['EV10']
    load_sce['EV20'] = load_sce['base'] + ev_load_data['EV20']
    load_sce['EV30'] = load_sce['base'] + ev_load_data['EV30']

    if ev_sce == 0:
        load = load_sce['base']
    elif ev_sce == 1:
        load = load_sce['EV1']
    elif ev_sce == 2:
        load = load_sce['EV5']
    elif ev_sce == 3:
        load = load_sce['EV10']
    elif ev_sce == 4:
        load = load_sce['EV20']
    elif ev_sce == 5:
        load = load_sce['EV30']

    load_all = load.to_dict()

    return load_all
