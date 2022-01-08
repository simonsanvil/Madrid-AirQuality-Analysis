indicators_code_dict = {
    1:{'parametro':'Dióxido de Azufre','abreviatura':'SO2','unidad':'µg/m 3','codigo_tecnica_de_medida':38,'tecnica_de_medida':'Fluorescencia ultravioleta'},
    6:{'parametro':'Monóxido de Carbono','abreviatura':'CO','unidad':'mg/m3','codigo_tecnica_de_medida':48,'tecnica_de_medida':'Absorción infrarroja'},
    7:{'parametro':'Monóxido de Nitrógeno','abreviatura':'NO','unidad':'µg/m 3','codigo_tecnica_de_medida':8,'tecnica_de_medida':'Quimioluminiscencia'},
    8:{'parametro':'Dióxido de Nitrógeno','abreviatura':'NO2','unidad':'µg/m 3','codigo_tecnica_de_medida':8,'tecnica_de_medida':'Id.'},
    9:{'parametro':'Partículas < 2.5 µm','abreviatura':'PM2.5','unidad':'µg/m3','codigo_tecnica_de_medida':47,'tecnica_de_medida':'Microbalanza'},
    10:{'parametro':'Partículas < 10 µm','abreviatura':'PM10','unidad':'µg/m3','codigo_tecnica_de_medida':47,'tecnica_de_medida':'Id.'},
    12:{'parametro':'Óxidos de Nitrógeno','abreviatura':'NOx','unidad':'µg/m3','codigo_tecnica_de_medida':8,'tecnica_de_medida':'Quimioluminiscencia'},
    14:{'parametro':'Ozono','abreviatura':'O3','unidad':'µg/m 3','codigo_tecnica_de_medida':6,'tecnica_de_medida':'Absorción ultravioleta'},
    20:{'parametro':'Tolueno','abreviatura':'TOL','unidad':'µg/m3','codigo_tecnica_de_medida':59,'tecnica_de_medida':'Cromatografía de gases'},
    30:{'parametro':'Benceno','abreviatura':'BEN','unidad':'µg/m3','codigo_tecnica_de_medida':59,'tecnica_de_medida':'Id.'},
    35:{'parametro':'Etilbenceno','abreviatura':'EBE','unidad':'µg/m3','codigo_tecnica_de_medida':59,'tecnica_de_medida':'Id.'},
    37:{'parametro':'Metaxileno','abreviatura':'MXY','unidad':'µg/m3','codigo_tecnica_de_medida':59,'tecnica_de_medida':'Id.'},
    38:{'parametro':'Paraxileno','abreviatura':'PXY','unidad':'µg/m3','codigo_tecnica_de_medida':59,'tecnica_de_medida':'Id.'},
    39:{'parametro':'Ortoxileno','abreviatura':'OXY','unidad':'µg/m3','codigo_tecnica_de_medida':59,'tecnica_de_medida':'Id.'},
    42:{'parametro':'Hidrocarburos totales','abreviatura':'TCH','unidad':'mg/m3','codigo_tecnica_de_medida':2,'tecnica_de_medida':'Ionización de llama'},
    43:{'parametro':'Metano','abreviatura':'CH4','unidad':'mg/m3','codigo_tecnica_de_medida':2,'tecnica_de_medida':'Id.'},
    44:{'parametro':'Hidrocarburos no metánicos','abreviatura':'NMHC','unidad':'mg/m3','codigo_tecnica_de_medida':2,'tecnica_de_medida':'Id.'},
    431:{'parametro':'MetaParaXileno','abreviatura':'MPX','unidad':'µg/m3','codigo_tecnica_de_medida':59,'tecnica_de_medida':'Id.'}
}


indicators_abbrev_dict = {
    'Dióxido de Azufre':'SO2','Monóxido de Carbono':'CO', 'Monóxido de Nitrógeno':'NO',
    'Dióxido de Nitrógeno':'NO2','Partículas < 2.5 µm':'PM2.5','Partículas < 10 µm':'PM10',
    'Óxidos de Nitrógeno':'NOx','Ozono':'O3','Tolueno':'TOL','Benceno':'BEN',
    'Etilbenceno':'EBE','Metaxileno':'MXY','Paraxileno':'PXY','Ortoxileno':'OXY',
    'Hidrocarburos totales':'TCH','Metano':'CH4','Hidrocarburos no metánicos':'NMHC'
}
indicators_abbrev_dict_rev = {v:k for k,v in indicators_abbrev_dict.items()}

#Diccionario de estaciones de Madrid en formato codigo:Nombre
estaciones_codes_dict = {
    1 : 'Pº. Recoletos',2:'Glta. de Carlos V',3:'Pza. del Carmen',4:'Pza. de España',
    5:'Barrio del Pilar', 6:'Pza. Dr. Marañón',7:'Pza. M. de Salamanca',8:'Escuelas Aguirre',
    9:'Pza. Luca de Tena',10:'Cuatro Caminos',11:'Av. Ramón y Cajal',12:'Pza. Manuel Becerra',
    13:'Vallecas',14:'Pza. Fdez. Ladreda',15:'Pza. Castilla',16:'Arturo Soria',17:'Villaverde Alto',
    18:'C/ Farolillo',19:'Huerta Castañeda',20:'Moratalaz',21:'Pza. Cristo Rey',22:'Pº. Pontones',
    23:'Final C/ Alcalá',24:'Casa de Campo',25:'Santa Eugenia',26:'Urb. Embajada (Barajas)',
    27:'Barajas',47:'Méndez Álvaro',48:'Pº. Castellana',49:'Retiro',50:'Pza. Castilla',
    54:'Ensanche Vallecas',55:'Urb. Embajada (Barajas)',56:'Plaza Elíptica',57:'Sanchinarro',
    58:'El Pardo',59:'Parque Juan Carlos I',60:'Tres Olivos',40:'Vallecas',35:'Pza. del Carmen',
    39:'Barrio del Pilar',38:'Cuatro Caminos',36:'Moratalaz',60:'Tres Olivos'
}