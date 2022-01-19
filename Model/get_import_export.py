
import pandas as pd

def im_ex_data(data_dir):
    import_export_data = pd.read_csv(data_dir + 'importexport_hourly.csv')
    import_export_data['total'] = import_export_data['importexport_1 (MW)'] + import_export_data['importexport_2 (MW)'] \
                                  + import_export_data['importexport_3 (MW)'] + import_export_data['importexport_4 (MW)'] \
                                  + import_export_data['importexport_5 (MW)']

    im_ex_all = import_export_data['total'].to_dict()

    return im_ex_all
