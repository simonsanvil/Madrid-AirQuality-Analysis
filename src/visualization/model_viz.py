from prophet.plot import add_changepoints_to_plot

from typing import Union

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import seaborn as sns

import statsmodels.api as sm

from ..models.prophet_utils import get_changepoints_from_model

def visualize_prophet_results(
    model_results,
    changepoints_threshold=0.25,
    nrows=2,
    ncols=1,
    ax_titles=None,
    start=None,end=None,
    with_changepoints=True,
    ):
    '''
    Visualize the results of a trained Prophet model.
    
    The plot shows the actual and forecasted values including significant changepoints
    obtained from the Prophet model during the train and test periods.

    Parameters
    ----------
    model_results : ModelResult
        NamedTuple obtained with the train_prophet_model function.
    changepoints_threshold : float
        Threshold to consider a changepoint as significant.
    nrows,ncols
        Number of rows and columns of the plot.
        If nrows*ncols==2 the plot will be split in two subplots
        with the first subplot showing the forecast in the entire period 
        and the second showing the actual values in the entire period.
    ax_titles : list of str
        Titles of the subplots.
    start,end : datetime.datetime
        Start and end of the period to be visualized.
    '''

    if nrows*ncols > 2:
        raise ValueError("The number of rows plus columns must be less than 3")
    if isinstance(ax_titles,str):
        ax_titles = [ax_titles]
    elif ax_titles is None:
        ax_titles = [None,None]
    m = model_results.model
    X_train, X_test = model_results.train_df, model_results.eval_df
    forecast = model_results.forecast_df
    r2 = model_results.eval_metrics_df['r2'].score

    
    if start is None:
        start = forecast.ds.min()
    if end is None:
        end = forecast.ds.max()
    
    X_train = X_train[X_train.ds.between(start,end)]
    X_test = X_test[X_test.ds.between(start,end)]
    forecast = forecast[forecast.ds.between(start,end)]

    X = X_train.append(X_test)
    fig, axes =  plt.subplots(nrows=nrows,ncols=ncols,figsize=(18,10),sharey=True,sharex=True)
    
    if nrows*ncols>1:
        # Plot the actual values in the test period as first plot
        ax = axes[0]
        ax.plot(X.ds,X.y,label="Actual")
        ax.fill_between(X_test.ds,ax.get_ylim()[0],ax.get_ylim()[1],color="orange",alpha=0.4,label="Test Period")
        ax.set_title(ax_titles[0])
        ax.legend(loc="upper left")
        ax = axes[1]
        ax.scatter(X_train.ds,X_train.y, color="black",label="Train",alpha=.6,zorder=3)
    else:
        ax = axes
        ax.scatter(X.ds,X.y,label="Actual",zorder=3)

    # Plot the actual and predicted values with confidence intervals
    if start!=model_results.eval_df.ds.min():
        ax.axvline(x=model_results.eval_df.ds.min(),color="green",label="Start of test period",alpha=.6,zorder=1)
    ax.plot(forecast.ds,forecast.yhat,color="royalblue",label=f"Forecast (r2={r2:.2f})",zorder=4)
    ax.fill_between(
        forecast.ds,forecast.yhat_lower,forecast.yhat_upper,
        color="cornflowerblue",
        label="Confidence Interval",
        alpha=0.5,
        zorder=2,
    )

    real_trend = sm.tsa.seasonal_decompose(X.set_index("ds")['y'], model='additive').trend
    predicted_trend = sm.tsa.seasonal_decompose(forecast.set_index("ds")['yhat'], model='additive').trend
    ax.plot(X.ds,real_trend,color="black",label="Real Trend")
    ax.plot(forecast.ds,predicted_trend,color="red",label="Predicted Trend")
    ax.legend(loc="upper right",ncol=2)
    if with_changepoints:
        # Plot the significant changepoints and trend
        changepoint_lines = add_changepoints_to_plot(ax,m,forecast,threshold=changepoints_threshold)
        changepoints = get_changepoints_from_model(m,threshold=changepoints_threshold)
        handles, labels = ax.get_legend_handles_labels()
        if len(changepoints)>0: 
            # If there were significant changepoints detected
            changepoint_handles = changepoint_lines[0]+[changepoint_lines[1]]
            changepoints_labels = ["trend",f"changepoints (th={changepoints_threshold:.2f})"]
        else:
            changepoint_handles, changepoints_labels = changepoint_lines[0], ["trend"]
        handles = handles + changepoint_handles
        labels = labels + changepoints_labels
        ax.legend(handles, labels,loc="upper right",ncol=2)
        ymin, ymax = ax.get_ylim()
        arrowprops = {'width': 1, 'headwidth': 1, 'headlength': 1, 'shrink':0.05 }
        # Annotate the changepoint vlines
        for cp in changepoints.values:
            ax.annotate(
                pd.to_datetime(str(cp)).strftime("%b-%d-%Y"),
                xy=(cp+pd.to_timedelta(12,'h'),ymin),
                xytext=(0,-20),
                textcoords='offset points',
                arrowprops=arrowprops,
                rotation=90, va='top', ha='center', annotation_clip=False
            ) 
    # else:
    #     #plot trend
    #     ax.plot(forecast.ds,forecast.trend,color="red",label="trend",alpha=0.5)
    #     ax.legend(loc="upper left",ncol=2)

    ax.set_title(ax_titles[-1])  
    fig.tight_layout()
    return fig,axes

def visualize_clasp_results(
    clasp_results,
    title=None,
    cp_format="%b-%d-%Y",
    **annotation_kwargs
    ):
    '''
    Visualize the sements obtained from a trained CLaSP model.

    Parameters
    ----------
    clasp_results : NamedTuple
        NamedTuple obtained with the train_clasp_model function.
    title : str
        Title of the plot.
    cp_format : str
        Format of the changepoint datetime labels. Must be a valid strftime format.
        Default: "%b-%d-%Y" for showing the month and day of the changepoint (e.g. "Feb-01-2021")
    **annotation_kwargs
        Keyword arguments to be passed to the annotate function
        for showing the dates of the changepoints in the plot.
    
    Returns
    -------
    fig,ax : matplotlib.figure.Figure, matplotlib.axes._subplots.AxesSubplot
        Figure and ax of the plot.
    '''
    ts_df = clasp_results.ts_df
    indicator = str(ts_df.columns[1])
    change_points_df = clasp_results.changepoints_df

    fig,ax = plt.subplots(figsize=(18,10))
    ax = sns.lineplot(data=ts_df,x="time",y=indicator,ax=ax,hue="segment")
    ax.set_xlim(ts_df.time.min(),ts_df.time.max() + pd.Timedelta(days=90)) 
    ymin, ymax = ax.get_ylim()
    arrowprops = {'width': 1, 'headwidth': 1, 'headlength': 1, 'shrink':0.05 }
    month_delta = pd.Timedelta(days=31)
    annotation_params = dict(
        xytext=(-12,-5),
        textcoords='offset points',
        arrowprops=arrowprops,
        rotation=55,va="top",ha="center",
        annotation_clip=False
    )
    annotation_params.update(annotation_kwargs)
    remove_ticks = set()
    for i,cp in enumerate(change_points_df.time):
        ax.axvline(
            cp,
            color="darkgrey",
            linestyle="--",
            linewidth=2,
            label="changepoints" if i==0 else None
        )
        ax.annotate(
            cp.strftime(cp_format),
            xy=(cp,ymin),
            **annotation_params
        )
        cp_year = int(cp.strftime("%Y"))
        if (cp - month_delta).year < cp_year:
            remove_ticks.add(cp.year)
        elif (cp + month_delta).year > cp_year:
            remove_ticks.add(cp.year+1)
    
    timestamp_ticks = pd.Series([pd.to_datetime(x,unit='D') for x in ax.get_xticks()])
    new_ticks = timestamp_ticks[[not any(np.abs(t-cp).days<60 for cp in change_points_df.time) for t in timestamp_ticks]]
    ax.set_xticks(new_ticks.values)
    ax.xaxis.set_major_formatter(dates.DateFormatter('%b\n%Y')) 
    ax.legend()
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[-1:], labels=labels[-1:],loc="upper right")
    ax.set(title=title,xlabel="")
    ax.grid(True)
    return fig, ax


def visualize_train_data(
    X:pd.DataFrame,
    y:str='y',
    eval_split_x:str = None,
    title:str = None,
    **kwargs
    ):
    """
    Visualize the train data with plotly.

    Parameters
    ----------
    X : pd.DataFrame
        Dataframe with the features. The index must be a datetime index.
    y : str, optional (default='y')
        Name of the target variable.
    eval_split_x : str, datetime, optional (default=None)
        Date when the data is split in train and test. 
        If None the split is not visualized.
    title : str or None, optional (default=None)
        Title of the plot.
    **kwargs
        Keyword arguments passed to the plotly.plot function.
    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        The Plotly figure.
    """
 
    fig = X.reset_index().plot(x=X.index.name,y=y,title=title)
    if kwargs:
        fig.update_layout(**kwargs)
    if eval_split_x:
        # add vertical line to plot to display the train and test split
        fig.add_vline(
                x=eval_split_x,
                line={"color": "red"},
                line_width=2,
                line_dash="dot",
        )
        fig.add_annotation(
                x=eval_split_x,
                y=1,
                text="Train-Test Split",
                yref="paper",
                arrowcolor="red",
        )
    return fig