import pandas as pd
import numpy as np


def weight_nearby_traffic(coord: tuple,km_dist: float,traffic_df: pd.DataFrame,traffic_locations_df: pd.DataFrame):
    '''
    Computes the weighted traffic intensity and average load of traffic stations nearby a given coordinate.

    Parameters
    ----------
    coord: tuple
        Coordinates of the point of interest (lat,long).
    km_dist: float
        Maximum distance in km to consider traffic stations.
    traffic_df: pandas.DataFrame
        Traffic data. E.g: Obtained from src.get_data.get_traffic_data().
    traffic_locations_df: pandas.DataFrame
        Traffic stations locations. E.g: Obtained from src.get_data.get_traffic_locations().
    
    Returns
    -------
    pandas.DataFrame
        Dataframe with the weighted traffic intensity and average load of traffic stations nearby a given coordinate.
    '''
    # Compute distance between traffic stations and point of interest
    km_distances = haversine_dist(coord[0],coord[1],traffic_locations_df.latitud,traffic_locations_df.longitud)
    # Filter those stations that are within km_dist of the point of interest
    traffic_stations_nearby = traffic_locations_df.loc[km_distances<=km_dist,["cod_cent"]]\
                                .assign(km_dist=km_distances[km_distances<=km_dist])\
                                    .set_index("cod_cent")
    # Weight the traffic intensity by the distance to the point of interest
    traffic_nearby_df = traffic_df\
        .loc[traffic_df.cod_cent.isin(traffic_stations_nearby.index)]\
            .join(
                traffic_stations_nearby,
                on="cod_cent",
                how="left"
            )
    traffic_nearby_df["weighted_intensity"] = traffic_nearby_df.intensidad*np.exp(-np.logaddexp(0, (traffic_nearby_df.km_dist-0.38)*15))
    avg_weighted_intensity = traffic_nearby_df.groupby("time").weighted_intensity.mean().rename("traffic_intensity")
    avg_traffic_load = traffic_nearby_df.groupby('time').carga.mean().rename("traffic_load")
    return pd.concat([avg_weighted_intensity,avg_traffic_load],axis=1)





def haversine_dist(long1,lat1,long2,lat2):
    '''
    Haversine formula to compute distance between two geographic point (lat,long)
    Return the distance in km from one point to another
    https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

    Parameters
    ----------
    long1,lat1: np.array or float
        Longitude and latitude of the first point(s). 
    long2,lat2: np.array or float
        Longitude and latitude of the second point(s).
        If an array is passed, must have the same shape as long1,lat1
        If a float, the distances are calculated between the point and all points in long1,lat1.

    Returns
    -------
    np.array
        Distance in km from one point to another.
    '''
    #convert decimal degrees to radians 
    long1_rad,lat1_rad,long2_rad,lat2_rad = map(np.radians,[long1,lat1,long2,lat2])
    
    #Apply haversine formula
    longdist = long1_rad-long2_rad
    latdist = lat1_rad-lat2_rad    
    a = np.sin(latdist/2)**2 + np.cos(lat1_rad)*np.cos(lat2_rad)*(np.sin(longdist/2)**2)
    c = 2 * np.arcsin(np.sqrt(a))

    #radius of earth is 6371km
    dist_km = 6371*c

    return dist_km