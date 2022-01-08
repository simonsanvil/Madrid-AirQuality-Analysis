import numpy as np
import pandas as pd


def preprocess_madrid_aq_data(df_raw,parameters_dict):
    '''
    Para realizar el preprocesado de datos de calidad de aire y meteorologicos de Madrid
    '''
    df = df_raw.copy()
    #Eliminar valores nulos de punto muestreo
    df.dropna(how='any',subset=['PUNTO_MUESTREO'],inplace=True)
    #Definir parametros leibles de acuerdo a la tabla de indicadores
    df['PARAMETRO'] = df.PUNTO_MUESTREO.apply(lambda x: parameters_dict[int(x.split('_')[1])]['parametro'])
    df['UNIDAD'] = df.PUNTO_MUESTREO.apply(lambda x: parameters_dict[int(x.split('_')[1])]['unidad'])
    #Obtener columna de fecha
    df['FECHA'] = df.ANO.astype(int).astype(str) + '-' + df.MES.astype(int).astype(str).str.zfill(2) + '-' + df.DIA.astype(int).astype(str).str.zfill(2)
    #Hacer un melt
    measurement_cols = df.columns[(df.columns.str.startswith('H'))]
    validation_cols = df.columns[(df.columns.str.startswith('V'))] 
    df = (
      df[['FECHA','PROVINCIA', 'MUNICIPIO', 'ESTACION', 'MAGNITUD','PARAMETRO','UNIDAD']+measurement_cols.tolist()+validation_cols.tolist()]
      .melt(['FECHA','PROVINCIA', 'MUNICIPIO', 'ESTACION', 'MAGNITUD','PARAMETRO','UNIDAD'])
    )
    #remover no validadas
    df = df[~((df.variable.str.startswith('V'))&(df.value!='V'))]
    df = df[df.variable.str.startswith('H')].rename(columns={'variable':'TIME'})
    #Unir Fecha y horas
    df['value'] = df['value'].astype(float)
    #Valores negativos deberian ser nans
    df['value'] = np.where(df['value']<0,0,df['value'])
    df['TIME'] = ''+df['TIME'].str.replace('H','').str.replace('24','00')+':00:00'
    df['FECHA'] = pd.to_datetime(df['FECHA'] + ' ' + df['TIME'])
    df = df.drop(columns='TIME')
    #Unir parametro y unidad
    df.columns=df.columns.str.lower().tolist()
    df['parametro'] = (df['parametro']+' ('+df['unidad']+')').str.lower()
    #Remover duplicados y unmelt
    df = (df
        .drop_duplicates(subset=['fecha','provincia','municipio','estacion','parametro','unidad'])
        .set_index(['fecha','provincia','municipio','estacion','parametro'])['value']
        .unstack()
        .reset_index().sort_values('fecha')
    )
    df.columns = df.columns.str.lower().tolist()
    return df

def unstack_calidad_aire_df(calidad_aire_df):
    calidad_aire_unstacked = (calidad_aire_df
         .copy()
         .set_index(['fecha','estacion','variable'])['value']
         .unstack()
         .sort_values('fecha')
         .reset_index()
         .rename_axis(columns=[''])
    )
    return calidad_aire_unstacked