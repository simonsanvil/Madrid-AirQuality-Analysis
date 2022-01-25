from prophet import Prophet
from sktime.annotation.clasp import ClaSPSegmentation, find_dominant_window_sizes

from collections import namedtuple
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time,logging
import statsmodels.api as sm

import contextlib, os

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__.split(".")[-1])
logger.setLevel(logging.INFO)

def train_prophet_model(
    madrid_df:pd.DataFrame,
    y:str,
    eval_start:str,
    train_start:str=None,
    eval_end:str=None,
    regressors:list = None,
    verbose:bool=True,
    **kwargs
    ):
    '''
    Trains a Prophet model for the given variable and data frame of madrid air quality.

    Parameters
    ----------
    madrid_df : pandas.DataFrame
        Dataframe with the air quality monitoring stations data.
    y : str
        Name of the variable to be predicted.
    eval_start : str or datetime.datetime
        Start date of the evaluation period.
    train_start : str or datetime.datetime, optional
        Start date of the train period.
        If None, the train period starts at the first date in the dataframe.
    eval_end : str, datetime.datetime, or TimeDelta optional
        End date of the evaluation period. 
        If None, the evaluation period is the period from eval_start to the end of the dataframe.
        If a timedelta is given, the evaluation period is the period from eval_start to eval_start + eval_end.
    regressors : list, optional
        List of regressors to be used in the model.
    verbose : bool, optional
        If True, prints info about the training process.
    **kwargs : dict
        Keyword arguments to be passed to the instance of the Prophet model.
    
    Returns
    -------
    ProphetResults
        NamedTuple with the following fields:
        - model : The trained Prophet model
        - train_df : pandas.DataFrame
            Dataframe with the train period.
        - eval_df : pandas.DataFrame
            Dataframe with the evaluation period.
        - forecast_df : pandas.DataFrame
            Dataframe with the forecast obtained with the model
            from predicting the entire available dates.
        - y_hat_df : pandas.DataFrame
            Dataframe with the forecast obtained with the model
            from predicting the evaluation period.
        - eval_metrics_df : pandas.DataFrame
            Dataframe with the metrics obtained from evaluating the model 
            on the evaluation period.
        - model_params : dict
            Dictionary with the parameters used to train the model (kwargs).
    '''
    if not verbose:
        logger.setLevel(logging.ERROR)
    # Make the namedtuple
    ProphetResults = namedtuple(
        "ProphetResults",["model","train_df","eval_df","forecast_df","y_hat_df","eval_metrics_df","model_params"]
    )

    madrid_df = madrid_df.copy()

    if y not in madrid_df.columns:
        raise ValueError(f'The variable "{y}" is not in the dataframe')
    if madrid_df.index.name=="time":
        madrid_df = madrid_df.reset_index()
    if train_start is None:
        train_start = madrid_df.time.min()
    if eval_end is None:
        eval_end = madrid_df.time.max()
    if isinstance(eval_end,pd.Timedelta):
        eval_end = pd.to_datetime(eval_start) + eval_end
    
     # Prepare the data for the prophet model
    X = madrid_df.set_index(
        "time"
    ).resample(
        "1D"
    ).mean().reset_index().rename(
        columns={"time":"ds",y:"y"}
    ).drop(
        columns=madrid_df.columns.intersection(["zone","zona","estacion","location"])
    ).copy()
    X = X[["ds","y"] + ([r for r in regressors] if regressors is not None else [])]
    X = X.set_index("ds").interpolate(limit=6).dropna().reset_index()
    # X = X.dropna(subset=["y"])
    
    # Train and evaluation split
    X_train = X[(X.ds<eval_start)&(X.ds>=train_start)].copy()
    X_test = X[(X.ds>=eval_start)&(X.ds<=eval_end)].copy()

    # Instantiate Prophet, fit model, and predict
    m = Prophet(**kwargs)
    # Add regressors
    if regressors is not None:
        for regressor in regressors:
            m.add_regressor(regressor)
    
    train_start = time.time()
    with suppress_stdout_stderr():
        m.fit(X_train)
    fit_time = time.time()-train_start
    logger.info(f"Model was fit in {fit_time:.2f} seconds. Making predictions...")
    
    # Make predictions
    forecast = m.predict(X_train.append(X_test))
    Y_hat = forecast.loc[forecast.ds.between(eval_start,eval_end),:]

    # Evaluate the model
    mse = mean_squared_error(X_test.y,Y_hat.yhat)
    mae = mean_absolute_error(X_test.y,Y_hat.yhat)
    r2 = r2_score(X_test.y,Y_hat.yhat)
    diff = np.mean((Y_hat.yhat.values - X_test.y.values)/Y_hat.yhat.values)

    # Evaluate the trend
    try:
        real_trend = sm.tsa.seasonal_decompose(X.set_index("ds")['y'], model='additive').trend
        predicted_trend = sm.tsa.seasonal_decompose(forecast.set_index("ds")['yhat'], model='additive').trend
        trend_diff = np.mean((predicted_trend - real_trend)/predicted_trend)
    except Exception as err:
        logger.warning(f"Could not evaluate the trend: {err}")
        trend_diff = np.nan

    logger.info(f"Evaluation complete. MSE={mse:.2f}, MAE={mae:.2f}, R2={r2:.2f}")
    logger.info(f"Mean difference between forecast and actual: {diff:+.2f}")

    metrics_df = pd.DataFrame(
        [mse,mae,r2,diff,trend_diff],
        index=["mse","mae","r2","mean_diff","trend_diff"],
        columns=["score"]
    ).T
    
    return ProphetResults(m, X_train, X_test, forecast, Y_hat, metrics_df, kwargs)

def train_clasp_model(
    madrid_df,
    y:str,
    location:str,
    location_by:str = 'zone',
    n_changepoints:int=10,
    period_length:int=None,
    train_start:str=None,
    train_end:str=None,
    verbose:bool=True,
    **kwargs
    ):
    '''
    Trains a CLaSP Time Series segmentation model for the given variable and data frame of madrid air quality measurements
    ClaSP is unsupervised so the model is trained on the entire training period provided.

    Parameters
    ----------
    madrid_df : pandas.DataFrame
        Dataframe with the air quality monitoring stations data.
    y : str
        Name of the variable to be predicted.
    location : str
        Name of the location to be predicted.
    location_by: str, optional
        Name of the column in the dataframe that contains the location names.
    n_changepoints : int, optional
        Max number of changepoints to attempt to detect.
    period_length : str, optional
        Period length to be used in the model.
        If None, the period length is the dominand window size of the time series.
    train_start : str or datetime.datetime, optional
        Start date of the train period.
        If None, the train period starts at the first date in the dataframe.
    train_end : str, datetime.datetime, or TimeDelta optional
        End date of the train period. 
        If None, the train period is the period from train_start to the end of the dataframe.
        If a timedelta is given, the train period is the period from train_start to train_start + train_end.
    verbose : bool, optional
        If True, prints info about the training process.
    **kwargs : dict
        Keyword arguments to be passed to the CLaSP model.
    
    Returns
    -------
    CLaSPResults
        NamedTuple with the following fields:
        - model : The trained CLaSP model
        - ts_df : pandas.DataFrame
            Time series Dataframe with the values of y for the training period
            and the segmentation obtained with the model.
        - changepoints_df : pandas.DataFrame
            Dataframe of changepoints detected by the model
            containing the time of each changepoint and its 
            associated score.
    '''
    ClaSPResults = namedtuple('ClaSPResults',['model','ts_df','changepoints_df'])
    if not verbose:
        logger.setLevel(logging.ERROR)
    if train_start is None:
        train_start = madrid_df.time.min()
    if train_end is None:
        train_end = madrid_df.time.max()
    # Make time series dataframe for ClaSPSegmentation
    df = madrid_df.copy().set_index(
        [location_by,"time"]
    ).groupby([pd.Grouper(level=location_by), 
                pd.Grouper(level='time', freq='1D')]
    ).mean().reset_index()
    # Convert to time series dataframe
    filter = (df[location_by]==location)&(df.time>=train_start)&(df.time<=train_end)
    ts_df = df[filter].set_index("time")\
                    .loc[:,y]\
                        .dropna()\
                            .sort_index().reset_index()
    if len(ts_df)==0:
        raise ValueError(f"No data for {y} at {location_by} {location} in the train period")
    # Extract the time series
    ts = ts_df[y]
    if period_length is None:
        try:
            period_length = find_dominant_window_sizes(ts)
        except Exception as err:
            logger.warning(f"Could not find a dominant window size for {y}. Using default of 10 days.")
            period_length = None
        if period_length is None:
            period_length = 10
    
    # Instantiate and fit the model
    logger.info(f"Training ClaSP model on timeseries of {y} data on {location_by} {location} with {n_changepoints} changepoints")
    train_start = time.time()
    clasp = ClaSPSegmentation(
        period_length=period_length,
        n_cps=n_changepoints, 
        fmt="sparse",
        **kwargs
    )
    found_changepoints = clasp.fit_predict(ts)
    fit_time = time.time()-train_start
    logger.info(f"Model was fit in {fit_time:.2f} seconds.")
    scores = clasp.scores

    if len(found_changepoints) == 1:
        if np.abs(ts_df.time[found_changepoints[0]] - ts_df.time.min()).days<30:
            found_changepoints = found_changepoints[1:]
        elif np.abs(ts_df.time[found_changepoints[0]] - ts_df.time.max()).days<30:
            found_changepoints = found_changepoints[1:]

    # Make dataframe of detected change points
    ts_df["segment"] = 0
    for i,cp in enumerate(found_changepoints.to_list()+[len(ts)]):
        lower_cp = found_changepoints[found_changepoints<cp].max()
        left = lower_cp if not pd.isnull(lower_cp) else 0
        ts_df.iloc[left:(cp),-1] = i
    
    if len(found_changepoints) == 0:
        logger.warning(f"No changepoints found for {y} at {location_by} {location} in the train period")
        logger.warning(f"Try with a different value for period_length")
        return ClaSPResults(clasp, ts_df, ts_df.iloc[[0],:])

    logger.info(f"{len(found_changepoints)} CHANGEPOINT(S) DETECTED")
    cps = list(set(found_changepoints.to_list()))
    change_points_df = ts_df.iloc[cps].copy()
    change_points_df["scores"] = scores

    return ClaSPResults(clasp, ts_df, change_points_df)

class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        for fd in self.null_fds + self.save_fds:
            os.close(fd)


