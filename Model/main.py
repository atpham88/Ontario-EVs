'''
An Pham
Economic Dispatch model for Ontario EVs project
Finished 01/19/2022

'''


import os
from pyomo.environ import *
from pyomo.opt import SolverFactory
import xlsxwriter as xw
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

from get_load_data import load_data
from get_re_data import renewable_data
from get_non_re_data import non_re_data
from get_import_export import im_ex_data
from get_hydro_cap import *

def main_params():
    ev_sce = 1                          # EV scenario to run
    hour = 8760
    day = 365
    cost_hydro = 3.3
    return ev_sce,hour,day,cost_hydro


def main_function():
    (ev_sce,hour,day,cost_hydro) = main_params()
    (data_dir,results_folder,solar_src_dir,solar_dst_dir,wind_src_dir,wind_dst_dir) = working_directory()
    (op_cost_non_re, pmin_non_re, cap_non_re, unit_non_re, name_non_re) = non_re_data(data_dir)
    (hydro_daily,unit_hydro_daily,hydro_daily_hcap,bi_mat_hydro,name_hydro_daily) = hydro_daily_cap(data_dir,day)
    (hydro_hourly, unit_hydro_hourly,name_hydro_hourly) = hydro_hourly_cap(data_dir,hour)
    (solar_cap, wind_cap, solar_name, wind_name, unit_solar,unit_wind) = renewable_data(data_dir, solar_src_dir, solar_dst_dir, wind_src_dir, wind_dst_dir,hour)
    (T,D,F,Hd,Hh,W,S) = main_sets(hour,day,unit_non_re,unit_hydro_daily,unit_hydro_hourly,unit_solar,unit_wind)
    im_ex_all = im_ex_data(data_dir)
    load_all = load_data(ev_sce, data_dir, day)
    model_solve(data_dir,results_folder,ev_sce,hour,day,T,D,F,Hd,Hh,W,S,im_ex_all,op_cost_non_re,load_all,cost_hydro,
                pmin_non_re, cap_non_re,hydro_daily,hydro_hourly,hydro_daily_hcap,bi_mat_hydro,name_hydro_hourly,name_hydro_daily,
                solar_cap,wind_cap,solar_name, wind_name,unit_non_re,name_non_re,unit_hydro_daily,unit_hydro_hourly,unit_solar,unit_wind)

def working_directory():
    data_dir = "C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Ontario-EVs\\Data Input\\"
    results_folder = "C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Ontario-EVs\\Results\\"
    solar_src_dir = "C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Ontario-EVs\\Data Input\\" \
                    "VRE_Resource_Analysis-ON\\Solar_Generation_Data\\"
    solar_dst_dir = "C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Ontario-EVs\\Data Input\\" \
                    "VRE_Resource_Analysis-ON\\solar_all\\"
    wind_src_dir = "C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Ontario-EVs\\Data Input\\" \
                   "VRE_Resource_Analysis-ON\\Wind_Generation_Data\\"
    wind_dst_dir = "C:\\Users\\atpha\\Documents\\Postdocs\\Projects\\Ontario-EVs\\Data Input\\" \
                   "VRE_Resource_Analysis-ON\\wind_all\\"
    return data_dir,results_folder,solar_src_dir,solar_dst_dir,wind_src_dir,wind_dst_dir


def main_sets(hour,day,unit_non_re,unit_hydro_daily,unit_hydro_hourly,unit_solar,unit_wind):
    T = list(range(hour))                       # Set of hours to run
    F = list(range(unit_non_re))
    Hd = list(range(unit_hydro_daily))
    Hh = list(range(unit_hydro_hourly))
    W = list(range(unit_wind))
    S = list(range(unit_solar))
    D = list(range(day))
    return T,D,F,Hd,Hh,W,S

def model_solve(data_dir,results_folder,ev_sce,hour,day,T,D,F,Hd,Hh,W,S,im_ex_all,op_cost_non_re,load_all,cost_hydro,
                pmin_non_re,cap_non_re,hydro_daily,hydro_hourly,hydro_daily_hcap,bi_mat_hydro,name_hydro_hourly,name_hydro_daily,
                solar_cap, wind_cap,solar_name,wind_name,unit_non_re,name_non_re,unit_hydro_daily,unit_hydro_hourly,unit_solar,unit_wind):

    model = ConcreteModel(name="Econ_Dispatch")

    # Define variables:
    model.g_F = Var(F,T,within=NonNegativeReals)                # non RE units generation
    model.g_Hd = Var(Hd,T,within=NonNegativeReals)              # hydro daily units generation
    model.g_Hh = Var(Hh,T,within=NonNegativeReals)              # hydro hourly units generation
    model.g_W = Var(W,T,within=NonNegativeReals)                # Wind units generation
    model.g_S = Var(S,T,within=NonNegativeReals)                # Solar units generation

    # Formulate constraints and  objective functions:
    # Constraints:
    # Meet demand constraint:
    def meet_demand(model, t):
        return sum(model.g_F[f, t] for f in F) + sum(model.g_Hd[d, t] for d in Hd) \
               + sum(model.g_Hh[h, t] for h in Hh) + sum(model.g_W[w, t] for w in W) \
               + sum(model.g_S[s, t] for s in S) + im_ex_all[t] == load_all[t]
    model.meet_demand_const = Constraint(T, rule=meet_demand)

    # Non RE unit constraints:
    def g_F_bound(model, f, t):
        return model.g_F[f, t] <= cap_non_re[f]
    model.g_F_bound_const = Constraint(F, T, rule=g_F_bound)

    # Minimum gen constraints:
    def g_F_min(model, f, t):
        return model.g_F[f, t] >= pmin_non_re[f]
    model.pmin_const = Constraint(F, T, rule=g_F_min)

    # Renewable (non-hydro) constraints:
    def g_W_bound(model, w, t):
        return model.g_W[w, t] <= wind_cap[w,t]
    model.g_W_bound_const = Constraint(W, T, rule=g_W_bound)

    def g_S_bound(model, s, t):
        return model.g_S[s, t] <= solar_cap[s,t]
    model.g_S_bound_const = Constraint(S, T, rule=g_S_bound)

    # Hydro gen constraints:
    # Hourly cap:
    def g_Hd_hourly_bound(model, d, t):
        return model.g_Hd[d, t] <= hydro_daily_hcap[d]
    model.g_Hd_hourly_bound_const = Constraint(Hd, T, rule=g_Hd_hourly_bound)

    def g_Hh_bound(model, h, t):
        return model.g_Hh[h, t] <= hydro_hourly[h,t]
    model.g_Hh_bound_const = Constraint(Hh, T, rule=g_Hh_bound)

    #Daily cap for daily hydro:
    def g_Hd_daily_bound(model, d, m):
        return sum(model.g_Hd[d, t]*bi_mat_hydro[d,t,m] for t in T) <= hydro_daily[d,m]
    model.g_Hd_daily_bound_const = Constraint(Hd, D, rule=g_Hd_daily_bound)

    # Objective function:
    def obj_function(model):
        return sum(model.g_F[f, t]*op_cost_non_re[f] for f in F for t in T) \
               + sum(model.g_Hd[d, t]*cost_hydro for d in Hd for t in T) \
               + sum(model.g_Hh[h, t]*cost_hydro for h in Hh for t in T)
    model.obj_func = Objective(rule=obj_function)

    # Solve the model and report results:
    model.dual = Suffix(direction=Suffix.IMPORT_EXPORT)
    solver = SolverFactory('cplex')
    results = solver.solve(model, tee=True)
    #model.pprint()

    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        print('Solution is feasible')
    elif (results.solver.termination_condition == TerminationCondition.infeasible):
        print('Solution is infeasible')
    else:
        # Something else is wrong
        print('Solver Status: ',  results.solver.status)

    print('Total Cost:', value(model.obj_func))

    # Print results:
    unit_non_re, unit_hydro_daily, unit_hydro_hourly, unit_solar, unit_wind
    g_F_star = np.zeros((unit_non_re, hour))
    g_Hd_star = np.zeros((unit_hydro_daily, hour))
    g_Hh_star = np.zeros((unit_hydro_hourly, hour))
    g_S_star = np.zeros((unit_solar, hour))
    g_W_star = np.zeros((unit_wind, hour))

    for f in F:
        for t in T:
            g_F_star[f, t] = value(model.g_F[f, t])

    for d in Hd:
        for t in T:
            g_Hd_star[d, t] = value(model.g_Hd[d, t])

    for h in Hh:
        for t in T:
            g_Hh_star[h, t] = value(model.g_Hh[h, t])

    for s in S:
        for t in T:
            g_S_star[s, t] = value(model.g_S[s, t])

    for w in W:
        for t in T:
            g_W_star[w, t] = value(model.g_W[w, t])

    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    if ev_sce == 0:
        case = 'basecase'
    elif ev_sce == 1:
        case = 'EV_1%'
    elif ev_sce == 2:
        case = 'EV_5%'
    elif ev_sce == 3:
        case = 'EV_10%'
    elif ev_sce == 4:
        case = 'EV_20%'
    elif ev_sce == 5:
        case = 'EV_30%'

    results_book = xw.Workbook(results_folder + 'OntarioEV_ED_' + case + '.xlsx')
    result_sheet_f = results_book.add_worksheet('Non-RE Non-Hydro Generation')
    result_sheet_hd = results_book.add_worksheet('Daily Hydro Generation')
    result_sheet_hh = results_book.add_worksheet('Hourly Hydro Generation')
    result_sheet_s = results_book.add_worksheet('Solar Generation')
    result_sheet_w = results_book.add_worksheet('Wind Generation')
    result_sheet_c = results_book.add_worksheet('Total cost')

    hour_number = [''] * hour
    for t in T:
        hour_number[t] = "hour " + str(T[t] + 1)

    # Write total cost result:
    total_cost = value(model.obj_func)
    result_sheet_c.write("A1", "Total Cost (Million $)")
    result_sheet_c.write("A2", total_cost / 1000000)

    # Write no re non hydro generation results:
    result_sheet_f.write("A1", "Plant ID")
    result_sheet_f.write("B1", "battery power rating (MW)")

    for item in F:
        result_sheet_f.write(item + 1, 0, name_non_re[item])

    for item in T:
        result_sheet_f.write(0, item + 1, hour_number[item])

    for item_1 in F:
        for item_2 in T:
            result_sheet_f.write(item_1 + 1, item_2 + 1, g_F_star[item_1, item_2])

    # Write hydro results:
    result_sheet_hd.write("A1", "Plant ID")
    result_sheet_hh.write("A1", "Plant ID")

    for item in Hd:
        result_sheet_hd.write(item + 1, 0, name_hydro_daily[item])

    for item in Hh:
        result_sheet_hh.write(item + 1, 0, name_hydro_hourly[item])

    for item in T:
        result_sheet_hd.write(0, item + 1, hour_number[item])
        result_sheet_hh.write(0, item + 1, hour_number[item])

    for item_1 in Hd:
        for item_2 in T:
            result_sheet_hd.write(item_1 + 1, item_2 + 1, g_Hd_star[item_1, item_2])

    for item_1 in Hh:
        for item_2 in T:
            result_sheet_hh.write(item_1 + 1, item_2 + 1, g_Hh_star[item_1, item_2])

    # Write renewable results:
    result_sheet_s.write("A1", "Plant ID")
    result_sheet_w.write("A1", "Plant ID")

    for item in S:
        result_sheet_s.write(item + 1, 0, solar_name[item])

    for item in W:
        result_sheet_w.write(item + 1, 0, wind_name[item])

    for item in T:
        result_sheet_s.write(0, item + 1, hour_number[item])
        result_sheet_w.write(0, item + 1, hour_number[item])

    for item_1 in S:
        for item_2 in T:
            result_sheet_s.write(item_1 + 1, item_2 + 1, g_S_star[item_1, item_2])

    for item_1 in W:
        for item_2 in T:
            result_sheet_w.write(item_1 + 1, item_2 + 1, g_W_star[item_1, item_2])

    results_book.close()

main_function()