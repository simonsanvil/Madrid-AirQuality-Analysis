import re
import numpy as np
import pandas as pd
from src.constants import MADRID_AIR_QUALITY_ZONES

zones_stations_dict = {
    estacion : zone
    for zone,estaciones in MADRID_AIR_QUALITY_ZONES.items() 
    for estacion in estaciones
}

def get_year_from_str(filename):
    if not isinstance(filename,str):
        return filename
    match = re.search('20[0-2][0-9]',filename)
    if match:
        span = match.span()
        return filename[span[0]:span[1]]
    return None

def group_df_by_zone(madrid_df):
    if "zone" not in madrid_df.columns:
        madrid_df["zone"] = madrid_df.estacion.replace(zones_stations_dict)
    df = madrid_df.copy().set_index(
        ["zone","time"]
    ).groupby([pd.Grouper(level='zone'), 
                pd.Grouper(level='time', freq='1D')]
    ).mean().reset_index()
    return df