import logging
import pandas as pd

from .preprocessing import weight_nearby_traffic
from .constants import MADRID_AIR_QUALITY_ZONES

logging.basicConfig()

def match_data(
    aq_df,
    weather_df=None,
    traffic_df=None,
    traffic_locations_df=None,
    air_locations_df=None,
    location_by="estacion",
    ) -> pd.DataFrame:
    '''
    Matches the data from air quality monitoring stations with meteorological data of cities in Madrid.
    Returns a pandas.Dataframe of the matched stations.
    '''
    aq_df = aq_df.copy()
    aq_df.columns = aq_df.columns.str.replace("µ","u")
    if traffic_df is not None and (air_locations_df is None or traffic_locations_df is None):
        logging.warning("No traffic or air stations locations dataframe provided. Traffic data will not be used.")
        traffic_df = None
    if traffic_df is None and weather_df is None:
        logging.warning("No weather or traffic dataframe provided. Nothing to match.")
        return aq_df
    if weather_df is not None:
        # Match the air quality monitoring stations with meteorological data
        aq_df = aq_df[aq_df.time.isin(weather_df.time)]\
            .join(
                weather_df.set_index("time"),
                on="time",
                how="left",
            ).dropna(subset=["time"])
    if traffic_df is not None:
        # Match the air quality monitoring stations with traffic data location by location    
        matched_dfs = []
        for location,lat,long in air_locations_df[[location_by,"latitud","longitud"]].values:
            location_df = aq_df[aq_df[location_by]==location]
            location_df = location_df[location_df.time.isin(traffic_df.time)]
            # Compute distance between air stations and traffic stations in km
            nearby_traffic_df = weight_nearby_traffic((lat,long),0.75,traffic_df,traffic_locations_df)
            avg_weighted_intensity = nearby_traffic_df["traffic_intensity"]
            avg_traffic_load = nearby_traffic_df["traffic_load"]
            # Join traffic data to air quality data
            location_df = location_df\
                .loc[(location_df.time.isin(avg_weighted_intensity.index))]\
                    .join(
                        pd.concat([avg_weighted_intensity,avg_traffic_load],axis=1),
                        on="time",
                        how="left"
                    ).dropna(subset=["time"])
            matched_dfs.append(location_df)
        madrid_air_quality_data = pd.concat(matched_dfs)
    else:
        return aq_df
    return madrid_air_quality_data.reset_index(drop=True)

def match_data_by_station(
        aq_df,
        weather_df=None,
        traffic_df=None,
    ) -> pd.DataFrame:
    '''
    Matches the data from air quality monitoring stations of the city of Madrid based on the air quality monitoring stations.
    Returns a dictionary of pandas.Dataframes of the matched stations dataframes.
    The keys of the dictionary are the names of the datasets of air quality monitoring stations.
    '''
    aq_air_dfs = {}
    # aq_station_datasets_names = {}
    for estacion in aq_df.estacion.unique():
        estacion_df = aq_df[aq_df.estacion==estacion].dropna(how="all",axis=1)\
                        .set_index("time")\
                            .interpolate(limit=6)
        estacion_df.columns = estacion_df.columns.str.replace("µ","u")
        if weather_df is not None:
            weather_estacion_df = weather_df.set_index("time")
            weather_estacion_df = weather_estacion_df.loc[weather_estacion_df.index.intersection(estacion_df.index)]
            estacion_df = estacion_df.loc[weather_estacion_df.index]
            weather_estacion_df = weather_estacion_df.loc[estacion_df.index]
            # Create the dataset of integrated weather/air-quality data for the given station
            estacion_df = pd.concat(
                [estacion_df,weather_estacion_df],axis=1
            ).rename_axis("time").reset_index().dropna(how='all',axis=1)
        if traffic_df is not None:
            traffic_estacion_df = traffic_df.set_index("time")
            traffic_estacion_df = traffic_estacion_df.loc[traffic_estacion_df.index.intersection(estacion_df.index)]
            estacion_df = estacion_df.loc[traffic_estacion_df.index]
            traffic_estacion_df = traffic_estacion_df.loc[estacion_df.index]
            # Create the dataset of integrated traffic/air-quality data for the given station
            estacion_df = pd.concat([estacion_df,traffic_estacion_df],axis=1).rename_axis("time").reset_index()
        aq_air_dfs[estacion] = estacion_df
        # aq_station_datasets_names[estacion] = dataset_name
    return aq_air_dfs

def match_data_by_zone(
        aq_df,
        weather_df=None,
        traffic_df=None,
    ) -> pd.DataFrame:
    '''
    Matches the data from air quality monitoring stations with meteorological data of cities in Madrid 
    based on the zones of the city of Madrid where the air quality monitoring stations are located.

    Returns a dictionary of pandas.Dataframes of the matched stations.
    The keys of the dictionary are the names of the zones of the city of Madrid and the values are the
    pandas.Dataframes of the matched stations.
    '''
    weather_df = weather_df.set_index("time")
    aq_df.columns = aq_df.columns.str.replace("µ","u")
    zones_dfs_dict = {}
    for zone,zones in MADRID_AIR_QUALITY_ZONES.items():
        zone_df = aq_df[aq_df.estacion.isin(zones)].set_index("time")
        if weather_df is not None:
            weather_zone_df = weather_df.loc[weather_df.index.intersection(zone_df.index)]
            zone_df = zone_df.loc[weather_zone_df.index]
            weather_zone_df = weather_zone_df.loc[zone_df.index]
            # Create the dataset of integrated weather/air-quality data for the given zone
            zone_df = pd.concat(
                [zone_df,weather_zone_df],axis=1
            ).rename_axis("time").reset_index().dropna(how='all',axis=1)
        zones_dfs_dict[zone] = zone_df
    return zones_dfs_dict