import pandas as pd
import numpy as np

# Get cost and parameters for non RE, non hydro units
def non_re_data(data_dir):
    silver_input = pd.read_excel(data_dir + 'SILVER Inputs.xlsx', sheet_name='Non-VRE Plants')
    silver_input = silver_input[silver_input["kind"].str.contains("importexport") == False]
    silver_input = silver_input[silver_input["name"].str.contains("hydro") == False]

    silver_input = silver_input.reset_index()
    silver_input = silver_input.drop('index',axis=1)

    op_cost_non_re = silver_input['Operating Cost ($/MWh)']
    pmin_non_re = silver_input['pmin (MW)']
    cap_non_re = silver_input['Capacity (MW)']
    name_non_re = silver_input['name']
    unit_non_re = len(silver_input)

    su_cost_non_re = np.zeros(unit_non_re)
    min_up_time = np.zeros(unit_non_re)
    min_down_time = np.zeros(unit_non_re)
    ramp_rate_non_re = np.zeros(unit_non_re)

    for i in list(range(len(name_non_re))):
        if 'nuclear' in name_non_re[i]:
            su_cost_non_re[i] = 55*cap_non_re[i]
            min_up_time[i] = 168
            min_down_time[i] = 24
            ramp_rate_non_re[i] = 0.01*cap_non_re[i]
        elif 'bio' in name_non_re[i]:
            su_cost_non_re[i] = 54*cap_non_re[i]
            min_up_time[i] = 8
            min_down_time[i] = 6
            ramp_rate_non_re[i] = 0.05*cap_non_re[i]
        elif 'NG_CC' in name_non_re[i]:
            su_cost_non_re[i] = 66*cap_non_re[i]
            min_up_time[i] = 8
            min_down_time[i] = 4
            ramp_rate_non_re[i] = 0.25*cap_non_re[i]
        elif 'NG_CT' in name_non_re[i]:
            su_cost_non_re[i] = 26*cap_non_re[i]
            min_up_time[i] = 1
            min_down_time[i] = 1
            ramp_rate_non_re[i] = 1*cap_non_re[i]
        elif 'NG_CG' in name_non_re[i]:
            su_cost_non_re[i] = 26*cap_non_re[i]
            min_up_time[i] = 1
            min_down_time[i] = 1
            ramp_rate_non_re[i] = 1*cap_non_re[i]

    su_cost_non_re = dict(enumerate(su_cost_non_re))
    min_up_time = dict(enumerate(min_up_time))
    min_down_time = dict(enumerate(min_down_time))
    ramp_rate_non_re = dict(enumerate(ramp_rate_non_re))

    op_cost_non_re = op_cost_non_re.to_dict()
    pmin_non_re = pmin_non_re.to_dict()
    cap_non_re = cap_non_re.to_dict()
    name_non_re = name_non_re.to_dict()

    return op_cost_non_re, pmin_non_re, cap_non_re, unit_non_re, name_non_re, \
           su_cost_non_re, min_up_time, min_down_time, ramp_rate_non_re