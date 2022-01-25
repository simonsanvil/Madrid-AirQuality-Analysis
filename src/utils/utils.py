import re
import numpy as np
import pandas as pd
from src.constants import MADRID_AIR_QUALITY_ZONES
import statsmodels.api as sm

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

def get_trend_difference(real,pred,model="additive"):
    """
    Compute the trend between real and predicted signal and calculate the 
    mean percentage deviation between the predicted trend and the real trend.

    % trend difference = 100*AVG{ (predicted_trend - real_trend)/predicted_trend }

    Parameters
    ----------
    real : pandas.Series or np.array
        Real signal.
    pred : pandas.Series or np.array
        Predicted/Forecasted signal.
    model : str, optional (default="additive")
        Seasonal model to be used.
    
    Returns
    -------
    float
        Percentage of deviation between the predicted trend and the real trend.
    """
    real_trend = sm.tsa.seasonal_decompose(real, model=model).trend
    predicted_trend = sm.tsa.seasonal_decompose(pred, model=model).trend
    trend_diff = np.mean((predicted_trend - real_trend)/predicted_trend)
    return trend_diff*100