import pandas as pd

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

    op_cost_non_re = op_cost_non_re.to_dict()
    pmin_non_re = pmin_non_re.to_dict()
    cap_non_re = cap_non_re.to_dict()
    name_non_re = name_non_re.to_dict()

    unit_non_re = len(silver_input)
    return op_cost_non_re, pmin_non_re, cap_non_re, unit_non_re, name_non_re