import pandas as pd
from functools import lru_cache
import glob, os, logging, difflib

from .preprocessing import clean_traffic_locations_raw
from .data_matching import match_data
from .extraction import extract_traffic_locations_raw
from .constants import MADRID_AIR_QUALITY_ZONES
logging.basicConfig()

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
    # Make zones column
    zones_stations_dict = {
        estacion : zone
        for zone,estaciones in MADRID_AIR_QUALITY_ZONES.items() 
        for estacion in estaciones
    }
    estaciones_calidad_aire_loc["zone"] = estaciones_calidad_aire_loc.estacion.replace(zones_stations_dict)
    return estaciones_calidad_aire_loc

@lru_cache
def get_traffic_locations_df(data_dir=".."):
    '''
    Returns a pandas.Dataframe of the geographical (latitude/longitude) points of each traffic monitoring station in the city of Madrid
    data_dir should be the path to the root data directory containing the raw and processed data of this project.
    e.g: get_traffic_locations_df(data_dir='../01-data')
    '''
    if not os.path.isfile(data_dir):
        fpaths = glob.glob(f'{data_dir}/**/traffic_locations_data.feather', recursive=True) 
        if not fpaths:
            logging.warning("Could not find the file traffic_locations_data.feather "\
                "in the directory tree of the data_dir specified. Using the raw data instead")
            fpaths = glob.glob(f'{data_dir}/**/pmed_trafico_ubicaciones_raw.feather', recursive=True)
            if not fpaths:
                logging.warning("Could not find the file pmed_trafico_ubicaciones_raw.feather "\
                    "in the directory tree of the data_dir specified. Extracting the raw data from source")
                traffic_locations_raw = extract_traffic_locations_raw()
            else:
                traffic_locations_raw = pd.read_feather(fpaths[0])
            traffic_locations_df = clean_traffic_locations_raw(traffic_locations_raw)
            return traffic_locations_df
        fpath = fpaths[0]
    else:
        fpath = data_dir
    
    return pd.read_feather(fpath)

@lru_cache
def get_air_quality_df(data_dir="..",meteo_normalized=False) -> pd.DataFrame:
    '''
    Returns a pandas.Dataframe of the air quality data of each air quality monitoring station in the city of Madrid
    data_dir should be the path to the root data directory containing the raw and processed data of this project.
    e.g: get_air_quality_df(data_dir='../01-data')

    meteo_normalized : bool, optional
        If True, the meteorological-normalized data will be returned if it is available.
    '''
    if not os.path.isfile(data_dir):
        if not meteo_normalized:
            fpaths = glob.glob(f'{data_dir}/**/air_quality_data.feather', recursive=True) 
        else:
            fpaths = glob.glob(f'{data_dir}/**/aq-weather_normalized.feather', recursive=True)
        if not fpaths:
            raise AttributeError("Could not find the file air_quality_data.feather in the directory tree of the data_dir specified")
        fpath = fpaths[0]
    else:
        fpath = data_dir
    
    return pd.read_feather(fpath)

@lru_cache
def get_weather_df(data_dir="..") -> pd.DataFrame:
    '''
    Returns a pandas.Dataframe of the meteorological data in the city of Madrid
    data_dir should be the path to the root data directory containing the raw and processed data of this project.
    e.g: get_weather_df(data_dir='../01-data')
    '''
    if not os.path.isfile(data_dir):
        fpaths = glob.glob(f'{data_dir}/**/weather_data.feather', recursive=True) 
        if not fpaths:
            raise AttributeError("Could not find the file weather_data.feather in the directory tree of the data_dir specified")
        fpath = fpaths[0]
    else:
        fpath = data_dir
    
    weather_df = pd.read_feather(fpath)    
    return weather_df

@lru_cache
def get_traffic_df(data_dir=".."):
    '''
    Returns a pandas.Dataframe of the traffic data in the city of Madrid
    data_dir should be the path to the root data directory containing the raw and processed data of this project.
    e.g: get_traffic_data_df(data_dir='../01-data')
    '''
    if not os.path.isfile(data_dir):
        fpaths = glob.glob(f'{data_dir}/**/traffic_data.feather', recursive=True) 
        if not fpaths:
            raise AttributeError("Could not find the file traffic_data.feather in the directory tree of the data_dir specified")
        fpath = fpaths[0]
    else:
        fpath = data_dir
    
    traffic_df = pd.read_feather(fpath).rename(
        columns={"fecha":"time"}
    ).loc[:,["time","nombre","cod_cent","id","intensidad","carga","ocupacion"]]
    traffic_df = traffic_df.loc[traffic_df.intensidad+traffic_df.ocupacion>=0,:]
    return traffic_df.dropna(subset=["time"])

@lru_cache
def get_madrid_data(data_dir="..",normalized=False):
    '''
    Returns a pandas.Dataframe of all weather, traffic, and meteorological data of the city of Madrid
    data_dir should be the path to the root data directory containing the raw and processed data of this project.
    e.g: get_madrid_data(data_dir='../01-data')
    '''
    if not os.path.isfile(data_dir):
        if not normalized:
            fpaths = glob.glob(f'{data_dir}/**/madrid_data.feather', recursive=True)
        else:
            fpaths = glob.glob(f'{data_dir}/**/madrid_normalized_data.feather', recursive=True)
            if not fpaths:
                raise AttributeError("Could not find the file madrid_normalized_data.feather in the directory tree of the data_dir specified")
        if not fpaths:
            logging.warning("Could not find the file madrid_air_quality_data.feather "\
                "in the directory tree of the data_dir specified. Attempting to make it instead")
            ### Air Quality Data
            aq_df = get_air_quality_df(data_dir)
            ### Weather data
            weather_df = get_weather_df(data_dir)
            ### Traffic data
            traffic_df = get_traffic_df(data_dir)
            ### Traffic locations
            traffic_locations_df = get_traffic_locations_df(data_dir)
            ### Air locations
            air_locations_df = get_air_locations_df(data_dir)
            # Match air quality stations with their locations
            close_matches = { est : difflib.get_close_matches(est,air_locations_df.estacion_aire.unique().tolist()) for est in aq_df.estacion.unique()}
            est_replacements = {old_est:matches[0] for old_est,matches in close_matches.items() if matches and old_est!=matches[0]}
            if est_replacements.get("Retiro") is None:
                est_replacements["Retiro"] = 'Parque del Retiro'
            aq_df["estacion"] = aq_df.estacion.replace(est_replacements)
            # Match and Merge the data
            return match_data(
                aq_df,
                weather_df,
                traffic_df,
                traffic_locations_df,
                air_locations_df
            )
        fpath = fpaths[0]
    else:
        fpath = data_dir
    
    return pd.read_feather(fpath)