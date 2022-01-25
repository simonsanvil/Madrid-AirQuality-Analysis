from scipy.interpolate import griddata
from shapely.geometry import Point
import osmnx as ox
from itertools import product
import matplotlib.pyplot as plt
import numpy as np

from ..get_data import get_air_locations_df

ox.config(use_cache=True, log_console=False)

def make_countoured_map_of_concentrations(
    madrid_df,
    indicator,
    geo_df = None,
    n_points=100j,
    title=None,
    ax = None,
    cmap = plt.cm.rainbow,
    vmin = None,
    vmax = None,
    get_cmap = False,
    ):
    '''
    Makes a map of the average concentration of a pollutant in Madrid
    the map is made by interpolating the data of the pollut to a regular grid
    and then plotting the data in a contour plot

    Parameters
    ----------
    madrid_df : pandas.DataFrame
        Dataframe with the data of the pollution in Madrid
    indicator : str
        Name of the pollutant to plot the concentration of
    geo_df : geopandas.DataFrame
        Geopandas Dataframe with the geometry of the map. If None, the map of Madrid is queried from OSM
    n_points : int
        Number of points to interpolate the data
    title : str
        Title of the plot
    ax : matplotlib.axes._subplots.AxesSubplot
        Axes to plot the map on. If None, a new figure is created
    cmap : matplotlib.colors.Colormap
        Colormap to use for the contour plot
    vmin : float
        Minimum value of the colorbar. If None, the minimum value of the data is used
    vmax : float
        Maximum value of the colorbar. If None, the maximum value of the data is used
    '''

    if 'latitud' not in madrid_df.columns or 'longitud' not in madrid_df.columns:
        air_locations = get_air_locations_df()
        madrid_df = madrid_df.merge(air_locations.set_index("estacion"),on="estacion")
    if geo_df is None:
        geo_df = ox.geocode_to_gdf('Madrid')

    df = madrid_df.groupby("estacion").mean().reset_index()
    
    x = df.longitud.values
    y = df.latitud.values
    z = df[indicator].values
    
    n,s,e,w = geo_df[["bbox_north","bbox_south","bbox_east","bbox_west"]].values[0]
    poly = geo_df.geometry.values[0]

    # define grid of coordinates
    xi, yi = np.mgrid[w:e:n_points,s:n:n_points]


    #Set exterior of polygon
    x_exterior_top, y_exterior_top = np.linspace(w,e,100), np.ones(100)*n
    x_exterior_bottom, y_exterior_bottom = np.linspace(w,e,100), np.ones(100)*s
    x_exterior_left, y_exterior_left = np.ones(100)*w, np.linspace(s,n,100)
    x_exterior_right, y_exterior_right = np.ones(100)*e, np.linspace(s,n,100)
    x_exterior = np.concatenate([x_exterior_top,x_exterior_bottom,x_exterior_left,x_exterior_right])
    y_exterior = np.concatenate([y_exterior_top,y_exterior_bottom,y_exterior_left,y_exterior_right])
    z_exterior = np.ones(len(x_exterior))*(min(z)-1)

    x,y,z = np.concatenate((x_exterior,x)), np.concatenate((y_exterior,y)), np.concatenate((z_exterior,z))

    # grid the data.
    zi = griddata((x, y), z, (xi, yi), method="linear")

    # remove those outside the polygon
    XYi = np.stack((xi,yi),axis=-1)
    inside = np.array([poly.contains(Point(XYi[a,b][0],XYi[a,b][1])) for a,b in product(range(0,xi.shape[0]),range(0,xi.shape[0]))])
    inside = inside.reshape(xi.shape)
    xi[~inside] = np.nan
    yi[~inside] = np.nan
    zi[~inside] = np.nan

    # Plot the map
    if ax is None:
        fig, ax = plt.subplots(figsize=(22,10))
    else:
        fig = None
    ax = geo_df.plot(ax=ax)

    # contour the gridded data
    if vmin is None:
        vmin = np.nanmin(zi)
    if vmax is None:
        vmax = np.nanmax(zi)
    CS = ax.contourf(xi,yi,zi,cmap=cmap ,alpha=0.5,vmin=vmin,vmax=vmax)
    if fig is not None:
        fig.colorbar(CS)
    # add data points.
    ax.scatter(df.longitud.values, df.latitud.values, marker='o', c='k', s=5, zorder=10)
    # ax.scatter(-3.7037,40.4158,color='white',marker='*',s=80) #Ayto Madrid

    # Format the map
    ax.set(title=title)
    ax.set_axis_off()
    
    if get_cmap:
        return ax,CS
    return ax