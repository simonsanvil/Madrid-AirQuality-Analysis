import pandas as pd
import numpy as np

from datetime import datetime as dt
import os

#To handle netcdf files
import netCDF4
from netCDF4 import num2date

def netcdf_to_pandas(fsource):
    # print("Processing netcdf file...")
    data = netCDF4.Dataset(fsource)
    data_vars = data.variables

    # Extract measurement variable
    var_names = [name for name in data_vars]

    var1 = data_vars[var_names[4]]

    dims = []
    for dim in var1.get_dims():
        if dim.name == "time":
            time_var = data_vars[dim.name]
            tstart = dt.strptime(time_var.units.split(" ")[-2],"%Y-%m-%d").strftime("%Y-%m-%d")
            time_unit = time_var.units + " since " + tstart
            times = num2date(time_var[:], time_unit,only_use_cftime_datetimes=False,only_use_python_datetimes=True)
            dims.append(times)
        elif dim.name=="longitude":
            longitudes = data_vars[dim.name][:]
            longitudes[longitudes>180] = -360 + longitudes[longitudes>180]
            dims.append(longitudes)
        else:
            dims.append(data_vars[dim.name][:])

    grids = [x.flatten() for x in np.meshgrid(*dims, indexing='ij')]

    dims_dict = {var1.dimensions[i]:grid for i,grid in enumerate(grids)}

    vars_dict = {
        var_name.split("_")[0] : data_vars[var_name][:].flatten() for var_name in var_names if var_name not in dims_dict
    }

    data_dict = {**dims_dict,**vars_dict}

    if 'level' in data_dict:
        data_dict.pop('level')

    df = pd.DataFrame(data_dict)
    df[['latitude','longitude']] = df[['latitude','longitude']].astype(float).round(4)
    nullrows = df[df.columns[~df.columns.isin(var1.dimensions)]].isnull().all(axis=1)
    df = df[~nullrows]

    # print("Process done.")
    return df