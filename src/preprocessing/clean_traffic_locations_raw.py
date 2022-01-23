import numpy as np
from pyproj import Proj
from pandas import DataFrame

def clean_traffic_locations_raw(pmed_ubicaciones_raw:DataFrame) -> DataFrame:
    '''
    Recibe un dataframe de ubicaciones de puntos de medida de trafico
    (como obtenido por `src.extraction.extract_traffic_locations_raw`) y lo procesa para 
    limpiarlo y tener solo dos columnas de informacion geografica (latitud y longitud) por cada punto de medida.
    '''

    #Proyeccion de coordendas utm de Madr (WGS84) Zona 30T E: 440291.27 N: 4474254.64
    projection = Proj("+proj=utm +zone=30 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

    #Procesar los datos raw para unir todos los datos geograficos y tener solo lat/long
    pmed_ubicaciones = pmed_ubicaciones_raw.copy()

    #Hay 3 tipos de columnas distintas que muestran coordenadas utm (utm_x/utm_y, x/y, coord_x/coord_y). Primero hay que juntarlas todas
    #Meter coord_x/coord_y dentro de utm_x/utm_y
    pmed_ubicaciones['utm_x'] = np.where(pmed_ubicaciones.utm_x.isnull(),pmed_ubicaciones.coord_x,pmed_ubicaciones.utm_x)
    pmed_ubicaciones['utm_y'] = np.where(pmed_ubicaciones.utm_y.isnull(),pmed_ubicaciones.coord_y,pmed_ubicaciones.utm_y)
    #Meter x/y dentro de utm_x/utm_y
    pmed_ubicaciones['utm_x'] = np.where(pmed_ubicaciones.utm_x.isnull(),pmed_ubicaciones.x,pmed_ubicaciones.utm_x)
    pmed_ubicaciones['utm_y'] = np.where(pmed_ubicaciones.utm_y.isnull(),pmed_ubicaciones.y,pmed_ubicaciones.utm_y)
    #Meter stx_x/st_y dentro de utm_x/utm_y
    pmed_ubicaciones['utm_x'] = np.where(pmed_ubicaciones.utm_x.isnull(),pmed_ubicaciones.st_x,pmed_ubicaciones.utm_x)
    pmed_ubicaciones['utm_y'] = np.where(pmed_ubicaciones.utm_y.isnull(),pmed_ubicaciones.st_y,pmed_ubicaciones.utm_y)

    #convertir coordenadas utm a coordenadas de latitud y longitud
    x_as_long, y_as_lat = projection(pmed_ubicaciones['utm_x'], pmed_ubicaciones['utm_y'],inverse=True)

    #La proyeccion devuelve NaNs como infinito (np.inf), los convertimos de nuevo a NaN para evitar problemas numericos
    x_as_long = np.where(x_as_long==np.inf,np.nan,x_as_long)
    y_as_lat = np.where(y_as_lat==np.inf,np.nan,y_as_lat)

    #llenar longitud y latitud con las nuevas coordenadas convertidas
    pmed_ubicaciones['longitud'] = np.where(pmed_ubicaciones.longitud.isnull(),x_as_long,pmed_ubicaciones.longitud)
    pmed_ubicaciones['latitud'] = np.where(pmed_ubicaciones.latitud.isnull(),y_as_lat,pmed_ubicaciones.latitud)

    #Eliminar columnas que usan coordenadas utm
    pmed_ubicaciones = pmed_ubicaciones.drop(columns=['utm_x','utm_y','x','y','coord_x','coord_y','st_x','st_y','geom'])
    
    pmed_ubicaciones["cod_cent"] = pmed_ubicaciones["cod_cent"].fillna(pmed_ubicaciones["nombre"])

    #Eliminar NaNs y columnas irrelevantes y asignar datatypes adecuados:
    pmed_ubicaciones = (
        pmed_ubicaciones
        .dropna(how='any',subset=['year','cod_cent'])
        .dropna(how='all',subset=['latitud','longitud'])
        .drop(columns=['distrito','id','idelem'])
        .astype(dtype={'latitud':float,'longitud':float,'cod_cent':str,'tipo_elem':str,'year':int})
        .drop_duplicates(subset=['cod_cent']) #solo ~1.4% de los puntos de medida se mueven significativamente a lo largo de los años
        .sort_values('year',ascending=False) 
        .reset_index(drop=True)
    )
    return pmed_ubicaciones