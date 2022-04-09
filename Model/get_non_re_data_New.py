import pandas as pd
import numpy as np

# Get cost and parameters for non RE, non hydro units
def non_re_data(data_dir):
    silver_input = pd.read_excel(data_dir + 'SILVER Inputs New.xlsx', sheet_name='Non-VRE Plants')
    silver_input = silver_input[silver_input["kind"].str.contains("importexport") == False]
    silver_input = silver_input[silver_input["name"].str.contains("hydro") == False]

    silver_input = silver_input.reset_index()
    silver_input = silver_input.drop('index',axis=1)

    op_cost_non_re = silver_input['Operating Cost ($/MWh)']
    pmin_non_re = silver_input['pmin (MW)']
    cap_non_re = silver_input['Capacity (MW)']
    name_non_re = silver_input['name']
    kind_non_re = silver_input['kind']
    unit_non_re = len(silver_input)

    su_cost_non_re = np.zeros(unit_non_re)
    min_up_time = np.zeros(unit_non_re)
    min_down_time = np.zeros(unit_non_re)
    ramp_rate_non_re = np.zeros(unit_non_re)

    for i in list(range(len(kind_non_re))):
        if 'nuclear' in kind_non_re[i]:
            su_cost_non_re[i] = 500*cap_non_re[i]
            min_up_time[i] = 20
            min_down_time[i] = 20
            ramp_rate_non_re[i] = 0.06*cap_non_re[i]
        elif 'biomass' in kind_non_re[i]:
            su_cost_non_re[i] = 100*cap_non_re[i]
            min_up_time[i] = 4
            min_down_time[i] = 4
            ramp_rate_non_re[i] = 1*cap_non_re[i]
        elif 'biogas' in kind_non_re[i]:
            su_cost_non_re[i] = 50*cap_non_re[i]
            min_up_time[i] = 4
            min_down_time[i] = 4
            ramp_rate_non_re[i] = 1*cap_non_re[i]
        elif 'NG_CC_1' in kind_non_re[i]:
            su_cost_non_re[i] = 66*cap_non_re[i]
            min_up_time[i] = 4
            min_down_time[i] = 4
            ramp_rate_non_re[i] = 0.66*cap_non_re[i]
        elif 'NG_CC_2' in kind_non_re[i]:
            su_cost_non_re[i] = 25*cap_non_re[i]
            min_up_time[i] = 4
            min_down_time[i] = 4
            ramp_rate_non_re[i] =0.3*cap_non_re[i]
        elif 'NG_CT_1' in kind_non_re[i]:
            su_cost_non_re[i] = 25*cap_non_re[i]
            min_up_time[i] = 1
            min_down_time[i] = 1
            ramp_rate_non_re[i] = 0.36*cap_non_re[i]
        elif 'NG_CT_2' in kind_non_re[i]:
            su_cost_non_re[i] = 25*cap_non_re[i]
            min_up_time[i] = 2
            min_down_time[i] = 2
            ramp_rate_non_re[i] = 0.36*cap_non_re[i]
        elif 'NG_CT_3' in kind_non_re[i]:
            su_cost_non_re[i] = 26*cap_non_re[i]
            min_up_time[i] = 3
            min_down_time[i] = 3
            ramp_rate_non_re[i] = 0.36*cap_non_re[i]
        elif 'NG_CG' in kind_non_re[i]:
            su_cost_non_re[i] = 100*cap_non_re[i]
            min_up_time[i] = 7
            min_down_time[i] = 7
            ramp_rate_non_re[i] = 0.24*cap_non_re[i]

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