import pandas as pd
import numpy as np
from functools import lru_cache
import glob, os

@lru_cache
def get_air_locations_df(data_dir=".."):
    '''
    Returns a pandas.Dataframe of the geographical (latitude/longitude) points of each air quality monitoring station in the city of Madrid
    
    data_dir should be the path to the root data directory containing the raw and processed data of this project.
    e.g: get_air_locations_df(data_dir='../01-data')
    '''
    #Path to location data
    if not os.path.isfile(data_dir):
        fpaths = glob.glob(f"{data_dir}/**/informacion_estaciones_red_calidad_aire.csv",recursive=True)
        if not fpaths:
            raise AttributeError("Could not find the file pmed_trafico_ubicaciones.feather in the directory tree of the data_dir specified")
        csv_path = fpaths[0]
    else:
        csv_path = data_dir
    estaciones_calidad_aire_loc = pd.read_csv(csv_path,encoding='latin-1',sep=';',decimal=',')
    estaciones_calidad_aire_loc.columns = estaciones_calidad_aire_loc.columns.str.lower()
    estaciones_calidad_aire_loc = estaciones_calidad_aire_loc\
                                    .filter(items = ['codigo_corto','estacion','latitud','longitud'])\
                                    .astype(dict(latitud=float,longitud=float,codigo_corto=int))
    estaciones_calidad_aire_loc = estaciones_calidad_aire_loc.rename(columns={'estacion':'estacion_aire'})
    return estaciones_calidad_aire_loc

@lru_cache
def get_traffic_locations_df(data_dir=".."):
    '''
    Returns a pandas.Dataframe of the geographical (latitude/longitude) points of each traffic monitoring station in the city of Madrid
    data_dir should be the path to the root data directory containing the raw and processed data of this project.
    e.g: get_traffic_locations_df(data_dir='../01-data')
    '''
    if not os.path.isfile(data_dir):
        fpaths = glob.glob(f'{data_dir}/**/pmed_trafico_ubicaciones.feather', recursive=True) 
        if not fpaths:
            raise AttributeError("Could not find the file pmed_trafico_ubicaciones.feather in the directory tree of the data_dir specified")
        fpath = fpaths[0]
    else:
        fpath = data_dir
    
    return pd.read_feather(fpath)
    