import re
import numpy as np

def get_year_from_str(filename):
    if not isinstance(filename,str):
        return filename
    match = re.search('20[0-2][0-9]',filename)
    if match:
        span = match.span()
        return filename[span[0]:span[1]]
    return None

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