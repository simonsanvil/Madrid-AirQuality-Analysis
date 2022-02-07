Air quality in the City of Madrid
===============================

Analysis of air-quality in the City of Madrid. A study the anthropogenic (human) factors that influence the concentration of pollutants in the air and the effects that historical administrative actions have had on the air quality.

The analysis here is based on statistical insights gathered from machine-learning models that have been trained with data collected from multiple monitoring stations located in the City of Madrid on a period of 7 years from 2014 to 2021.

<br>

![Average concentration of NO2 2020 vs 2021](/reports/figures/map_avg_concentrations_no2_2020-2021.png?raw=true)


Data Sources
-------------

Various data sources were used throughout this analysis. Most of the city-level data was obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) del Ayuntamiento de Madrid. 

The following datasets were built to carry out most of the analysis:

- **Air quality data**: the air quality measurements were obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) of the City of Madrid. Contains hourly-averaged air quality measurements for each air-quality monitoring station in the city from 2014 to 2021.

- **Traffic data**: All traffic-related data was obtained from the [Portal de Datos Abiertos](https://datos.madrid.es/portal) of the City of Madrid. Contains hourly-averaged traffic data for each measurement point of traffic in the city from 2014 to 2021.

- **Meteorological data**: Meteorological data was collected from the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form). Contains city-wide hourly values of weather variables such as temperature, precipitation, wind speed, and cloud cover from 2014 to 2021.

Techniques Used
-------------

### Meteorological Normalization using Random Forests

It is somewhat intuitive to understand how weather plays an important factor in the air pollution at a certain location. Things like the velocity and direction at which air moves can be directly correlated to spikes in the particle-matter concentrations in an area. Significant variations in temperature thoughout a period can change the way chemical compounds such as NO2 react with other gases and break down. 
 
In order to better analyze anthropogenic pollutant emissions (emissions caused by humans), it is important to discount the effect that weather has on these emissions, the process of removing the effects of weather in a time series is known in the literature as meteorological normalization. 

I've used the [`rmweather`](https://github.com/skgrange/rmweather) package which uses a technique developed by [Grange et al.](https://www.atmos-chem-phys.net/18/6223/2018/) to perform the meteorological normalization. The way it works is that a random forest model is trained to predict each pollutant to normalize based on the meteorological features available. Then, for each observation of the pollutant hundreds of predictions are made, each time sampling the explanatory variables without replacement and finally aggregating them using the arithmetic mean. When the process is finished, the aggregated observations become the new meteorologically-normalized time series.


| ![Meteorological Normalization before and after](/reports/figures/meteo-normalization-before-after.jpeg?raw=true) |
|:--:| 
| NO2 concentrations in the downtown area before (left) and after (right) performing Meteorological Normalization, we can clearly see how [Madrid Central](https://en.wikipedia.org/wiki/Madrid_Central) (implemented in late 2018) reduced the levels of this pollutant significantly. |



### Time Series Segmentation using ClaSP and Trend analysis with Prophet

Time Series segmentation can be used to automatically detect changepoints in the historical data of pollutant concentrations in the city. This is useful if we can relate changepoints to times when administrative actions have been taken and enable us to find out which where the ones that produced a measureable effect. [ClaSP](https://dl.acm.org/doi/abs/10.1145/3459637.3482240) (Classification Score Profile) is a novel unsupervised technique to do Time Series Segmentation automatically. 

Another way to measure the impact that certain actions have on air pollution is to analyze the trend of the concentrations of a pollutant before and after the action was implemented. This analysis can be further enhanced by making an estimation of what the trend would have been had that action never taken place. If the action truly had an impact on the air quality we would expect that the deviation between the line of the estimated trend and the line real trend be significantly different after the point of interest. 

For this analysis I make use of [Prophet](https://github.com/facebook/prophet) ([Taylor S, Letham B., 2018](https://peerj.com/preprints/3190.pdf)) to perform trend estimation to forecast the time series of daily average concentrations of a pollutant at a given zone after the occurrence of a changepoint and then compare the trend of the obtained prediction with the actual trend before and after a changepoint to quantify the deviation in air pollution produced from that change. 


| ![TS Segmentation of Normalized NO2 on Zone 1](/reports/figures/meteo_normalized_and_cps_no2_zone1.png?raw=true) | ![Forecast of NO2 on Zone 1](/reports/figures/forecast_trend_no2_zone1.png?raw=true) |
|:--:|  :--: |
| Example of using ClaSP on the meteorologically-normalized series of NO2 concentrations. The first changepoint can be attributed to Madrid Central, the second and third to the COVID-19 pandemic | Example of performing forecast and trend analysis with Prophet on the time-series of pollutant concentrations after a certain changepoint (The Covid-19 Lockdown). The real trend was about 18% lower than the one estimated if the changepoint had not ocurred   |

Data Pipeline
-------------

#TODO

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
