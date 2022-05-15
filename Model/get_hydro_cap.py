
import pandas as pd
import numpy as np

def hydro_hourly_cap(data_dir,hour,starting_hour):
    hydro_hourly_data = pd.read_csv(data_dir + 'hydro_hourly capacity.csv')
    hydro_hourly_data = hydro_hourly_data.rename({'hydro_hourly_1 (MW)': 'hydro_hourly_1',
                                                  'hydro_hourly_2 (MW)': 'hydro_hourly_2',
                                                  'hydro_hourly_3 (MW)': 'hydro_hourly_3',
                                                  'hydro_hourly_4 (MW)': 'hydro_hourly_4',
                                                  'hydro_hourly_5 (MW)': 'hydro_hourly_5',
                                                  'hydro_hourly_6 (MW)': 'hydro_hourly_6',
                                                  'hydro_hourly_7 (MW)': 'hydro_hourly_7',
                                                  'hydro_hourly_8 (MW)': 'hydro_hourly_8',
                                                  'hydro_hourly_9 (MW)': 'hydro_hourly_9',
                                                  'hydro_hourly_10 (MW)': 'hydro_hourly_10'}, axis=1)
    hydro_hourly_data_T = hydro_hourly_data.T
    hydro_hourly_data_T = hydro_hourly_data_T.reset_index()
    name_hydro_hourly = hydro_hourly_data_T['index']
    hydro_hourly_data_T = hydro_hourly_data_T.drop('index', 1)
    hydro_hourly_data_T = hydro_hourly_data_T.iloc[:,starting_hour:starting_hour+hour]
    hydro_hourly_data_T.columns = pd.RangeIndex(0, len(hydro_hourly_data_T.columns))

    hydro_hourly = {(r, c): hydro_hourly_data_T.at[r, c] for r in list(range(len(hydro_hourly_data_T))) for c in list(range(hour))}
    unit_hydro_hourly = len(hydro_hourly_data_T)

    return hydro_hourly, unit_hydro_hourly, name_hydro_hourly

def hydro_daily_cap(data_dir,day,hour,starting_hour,starting_day):
    hydro_daily_data = pd.read_csv(data_dir + 'hydro_daily budget.csv')
    hydro_daily_data = hydro_daily_data.rename({'hydro_daily_1 (MW)': 'hydro_daily_1',
                                                 'hydro_daily_2 (MW)': 'hydro_daily_2',
                                                 'hydro_daily_3 (MW)': 'hydro_daily_3',
                                                 'hydro_daily_4 (MW)': 'hydro_daily_4',
                                                 'hydro_daily_5 (MW)': 'hydro_daily_5'}, axis=1)
    hydro_daily_data = hydro_daily_data.drop('date',1)
    hydro_daily_data_T = hydro_daily_data.T
    hydro_daily_data_T = hydro_daily_data_T.reset_index()
    name_hydro_daily = hydro_daily_data_T['index']
    hydro_daily_data_T = hydro_daily_data_T.drop('index', 1)
    hydro_daily_data_T = hydro_daily_data_T.iloc[:,starting_day:starting_day+day]
    hydro_daily_data_T.columns = pd.RangeIndex(0, len(hydro_daily_data_T.columns))

    hydro_daily = {(r, c): hydro_daily_data_T.at[r, c] for r in list(range(len(hydro_daily_data_T))) for c in list(range(day))}

    hydro_daily_hcap = {0:23, 1:206, 2:928, 3:1662, 4:1274}

    unit_hydro_daily = len(hydro_daily_data_T)

    bi_mat_hydro = np.zeros((unit_hydro_daily, hour, day))
    one_mat_hydro = np.ones((unit_hydro_daily, 24))

    count1 = 0
    count2 = 24
    for j in list(range(day)):
        bi_mat_hydro[:,count1:count2,j] = one_mat_hydro
        count1 = count1 + 24
        count2 = count2 + 24

    return hydro_daily,unit_hydro_daily,hydro_daily_hcap,bi_mat_hydro,name_hydro_daily

def hydro_monthly_cap(data_dir, hour, month, starting_month):
    hydro_monthly_data = pd.read_csv(data_dir + 'hydro_monthly budget.csv')
    hydro_monthly_data = hydro_monthly_data.drop('date', 1)
    hydro_monthly_data_T = hydro_monthly_data.T
    hydro_monthly_data_T = hydro_monthly_data_T.reset_index()
    name_hydro_monthly = hydro_monthly_data_T['index']
    hydro_monthly_data_T = hydro_monthly_data_T.drop('index', 1)
    hydro_monthly_data_T = hydro_monthly_data_T.iloc[:, starting_month:starting_month + month]
    hydro_monthly_data_T.columns = pd.RangeIndex(0, len(hydro_monthly_data_T.columns))

    hydro_monthly = {(r, c): hydro_monthly_data_T.at[r, c] for r in list(range(len(hydro_monthly_data_T))) for c in list(range(month))}
    hydro_monthly_hcap = {0: 23, 1: 206, 2: 928, 3: 1662, 4: 1274, 5: 1274}
    unit_hydro_monthly = len(hydro_monthly_data_T)
    bi_mat_hydro_m = np.zeros((unit_hydro_monthly, hour, month))

    count1 = 0
    count2 = [31,28,31,30,31,30,31,31,30,31,30,31]
    count2 = [element * 24 for element in count2]
    for j in list(range(month)):
        one_mat_hydro = np.ones((unit_hydro_monthly, count2[j]))
        if j == 0:
            bi_mat_hydro_m[:, count1:count2[j], j] = one_mat_hydro
            count3 = count2[j] + count2[j + 1]
        else:
            bi_mat_hydro_m[:, count1:count3, j] = one_mat_hydro
            if j < list(range(month))[-1]:
                count3 = count3 + count2[j + 1]
        count1 = count1 + count2[j]

    return hydro_monthly, unit_hydro_monthly, hydro_monthly_hcap, bi_mat_hydro_m, name_hydro_monthly