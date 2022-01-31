Air quality in the City of Madrid
===============================

Analysis of air-quality in the City of Madrid. A study the factors that influence the concentration of pollutants in the air and the effects that certain social or administrative actions can have on the air quality.

The analysis here is based on statistical insights gathered from machine-learning models that have been trained with data collected from multiple monitoring stations located in the City of Madrid on a period of 7 years from 2014 to 2021.


Data Sources
-------------

Various data sources were used throughout this analysis. Most of the city-level data was obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) del Ayuntamiento de Madrid. 

The following datasets were built to carry out most of the analysis:

- **Air quality data**: the air quality measurements were obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) of the City of Madrid. Contains hourly-averaged air quality measurements for each air-quality monitoring station in the city from 2014 to 2021.

- **Traffic data**: All traffic-related data was obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) of the City of Madrid. Contains hourly-averaged traffic data for each measurement point of traffic in the city from 2014 to 2021.

- **Meteorological data**: Meteorological data was collected from the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form). Contains city-wide hourly values of weather variables such as temperature, precipitation, wind speed, and cloud cover from 2014 to 2021.


- **Demographics data**: the population data were obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) of the City of Madrid. Contains the population of the city from 2014 to 2021.


Reproducibility
-----------

If you are interested in reproducing the results of this analysis, you can follow the steps below:

1. Clone this [GitHub repository]()
2. Extract the data used in the analysis from the Portal de Datos Abiertos. The `references` folder contains information about where to obtain the raw data from there.
3. Take a look and execute the jupyter notebooks in the `notebooks` folder in the given order to reassess the analysis.

Contact me or create an issue in this repository if you have any questions or comments.

Acknowledgements:
-----

This work was made as part of my course work for the *Data Science Project* subject of the Bachelors of Data Science and Engineering degree at the University Carlos III de Madrid. This work was supervised by professor Harold Molina-Bulla Ph.D and the course was supervised by professor Fernando Diaz de María Ph.D. 

This project was as part of a cooperation between the university and the Madrid city town-hall (Ayuntamiento de Madrid). Special aknowlegements to Honorio Enrique Crespo Díaz Alejo, Francisco José López Carmona, and David Garcia Falin from Ayuntamiento de Madrid for their support throughout this project.
