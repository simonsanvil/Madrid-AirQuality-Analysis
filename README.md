Air quality in the City of Madrid
===============================

Analysis of air-quality in the City of Madrid. We study the factors that influence the concentration of pollutants in the air and the effects that certain social or administrative actions can have on the air quality.

We base our analysis and conclusions on statistical insights gathered from machine-learning models that have been trained with data collected from multiple monitoring stations located in the City of Madrid on a period of 7 years from 2014 to 2021.

Authors:
--------

- [Simon E. Sanchez Viloria](https://github.com/simonsanvil)
- [Ines Olmos Alonzo]()
- [Francisco Javier Icaza Navarro]()
- [Paloma Sahelices Soto]()

Data Sources
-------------

Various data sources were used throughout our analysis. Most of the city-level data was obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) del Ayuntamiento de Madrid. 

The following datasets were built to carry out most of the analysis:

- **Air quality data**: the air quality measurements were obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) of the City of Madrid. Contains hourly-averaged air quality measurements for each air-quality monitoring station in the city from 2014 to 2021.

- **Traffic data**: All traffic-related data was obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) of the City of Madrid. Contains hourly-averaged traffic data for each measurement point of traffic in the city from 2014 to 2021.

- **Meteorological data**: Meteorological data was collected from the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form). Contains city-wide hourly values of weather variables such as temperature, precipitation, wind speed, and cloud cover from 2014 to 2021.


- **Demographics data**: the population data were obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) of the City of Madrid. Contains the population of the city from 2014 to 2021.


Full Report
------------------------

We wrote a comprehensive report of the methodology and results of our analysis. This report is available in pdf format in [here]() as well as in the [reports]() folder of this repository. 

Dashboard
---------

Additional to the report, an interactive dashboard was built to present and visualize the key results of our analysis. The dashboard is divided into three sections:

1.
2.
3.

This dashboard was built using [streamlit](https://streamlit.io/) and is available at [https://streamlit...]().

Reproducibility
-----------

If you are interested in reproducing the results of our analysis, you can follow the steps below:

1. Clone the [GitHub repository]()
2. Extract the data used in our analysis from the Portal de Datos Abiertos. The `references` folder contains information about where to obtain the raw data from there.
3. Take a look and execute the jupyter notebooks in the `notebooks` folder in the given order.
4. Run the streamlit app in the `dashboard` folder to see the results of the analysis.

Contact us or create an issue in this repository if you have any questions or comments.

Acknowledgements:
-----

This work was made as part of our course for the *Data Science Project* of the Bachelors of Data Science and Engineering degree at the University Carlos III de Madrid. Our work was supervised by professor Harold Molina-Bulla Ph.D and the course was supervised by professor Fernando Diaz de María Ph.D. 

This work was as part of a cooperation between the university/students and the Madrid city town-hall (Ayuntamiento de Madrid). Special aknowlegements to Honorio Enrique Crespo Díaz Alejo, Francisco José López Carmona, and David Garcia Falin from Ayuntamiento de Madrid for their support throughout our work.

References
--------
