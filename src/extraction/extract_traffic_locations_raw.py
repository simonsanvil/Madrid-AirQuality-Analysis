import requests, zipfile, io
import os

import pandas as pd

from fastprogress import progress_bar
from simpledbf import Dbf5

from ..constants import pmed_ubicaciones_source_str
from ..utils import get_year_from_str

def extract_traffic_locations_raw():
    '''
    Retrieves the raw data containing the locations of the traffic measurement stations in the city of Madrid directly from datos.madrid.es webpage and returns it as a pandas.DataFrame.
    '''
    url_ficheros = [w for w in pmed_ubicaciones_source_str.split(' ') if w.startswith('https://') and w.endswith('.zip')]
    trafico_locations_dfs = []
    print(f"Intentando obtener datos de puntos de medida de trafico desde sus ficheros en https://datos.madrid.es. Esto podria demorarse un rato...")
    filecount = 0
    for url in progress_bar(url_ficheros):
        resp = requests.get(url)
        if not resp.ok:
            print(f"Request failed for url {url}")
            continue
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        files = [f.filename for f in z.filelist]
        ffound = 0
        for filename in files:
            if filename.endswith('.csv'):
                df = pd.read_csv(z.open(filename),encoding='latin-1',sep=';',decimal=',')
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(z.open(filename))
            elif filename.endswith('.dbf'):
                extracted_path = z.extract(filename)
                df = Dbf5(filename,codec='latin-1').to_dataframe()
                os.remove(filename)
            else:
                continue
            df.columns = df.columns.str.lower()
            if url == 'https://datos.madrid.es/egob/catalogo/202468-3-intensidad-trafico.zip' and filename=='pmed_trafico.dbf':
                df['filename'] = 'pmed_ubicacion_06-2017'
            else:
                df['filename'] = filename
            trafico_locations_dfs.append(df)            
            print(f"Se han leido {len(df)} filas de datos del archivo {filename}. ({sum(len(df) for df in trafico_locations_dfs)} observaciones en total)",end='\r')            
            ffound += 1
            break
        filecount += ffound
    print(f"Un total de {filecount} archivos han sido leidos con exito de {len(url_ficheros)} ficheros en la pagina web de datos de intensidad de trafico de Madrid")
    pmed_ubicaciones_raw = pd.concat(trafico_locations_dfs).reset_index(drop=True).astype({'tipo_elem':str})
    pmed_ubicaciones_raw = pmed_ubicaciones_raw.drop_duplicates(subset=pmed_ubicaciones_raw.columns.difference(['filename']))
    pmed_ubicaciones_raw['year'] = pmed_ubicaciones_raw.filename.apply(get_year_from_str)
    pmed_ubicaciones_raw = pmed_ubicaciones_raw.drop(columns='filename').reset_index(drop=True)
    pmed_ubicaciones_raw = pmed_ubicaciones_raw.astype(dict(x=float,y=float,st_x=float,st_y=float,year=int,tipo_elem=str))
    
    return pmed_ubicaciones_raw 
    # pmed_ubicaciones_raw.to_feather('../01-data/interim/pmed_ubicaciones_raw.feather')