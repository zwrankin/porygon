porygon
==============================
<img src="gallery/porygon.png" alt="drawing" width="120"/>

A library for making beautiful maps from geospatial data.  
- Internally coherent data structures that connect the data manipulation of [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) & [`geopandas.GeoDataFrame`](http://geopandas.org/data_structures.html#geodataframe) with the plotting library [`folium`](https://python-visualization.github.io/folium/). 
- Streamlined aggregation of point data to polygons by providing a consistent interface over geospatial tools such as [`h3`](https://uber.github.io/h3/#/), [`shapely`](https://shapely.readthedocs.io/en/stable/index.html), [`scipy.Voronoi`](https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.spatial.Voronoi.html), and more. 
- First-class plotting methods of `PorygonDataFrame` that streamline data transformations and provide additional plotting utilities (e.g. custom legends) beyond folium. 


## Motivating Example
Using the >200,000 [Chicago Traffic Accidents from 2019](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if), which parts of the City have proclivities toward different vehicle makes? (See [Quickstart](https://github.com/zwrankin/porygon/blob/master/notebooks/Quickstart.ipynb) for analysis code, and [Gallery](https://github.com/zwrankin/porygon/tree/master/gallery) for interactive html and more examples)
![Accidents by Make](gallery/traffic_accidents_by_make.png?raw=true "Accidents by Make")


## Getting started
Until more formal documentation is available, start by reading the [`Quickstart jupyter notebook`](https://github.com/zwrankin/porygon/blob/master/notebooks/Quickstart.ipynb)


## [Gallery](https://github.com/zwrankin/porygon/tree/master/gallery  )
*See gallery for interactive html files, not currently able to render in Github*


## Installation 
Not available from [pypi](https://pypi.org/), you must clone and install locally.  
```
conda create -n porygon python=3.7 pip
conda activate porygon
cd porygon && python setup.py develop
```
*NOTE* - if you are having trouble with the h3 installation, you may need to manually `pip install cmake`.  
If running the `Quickstart` notebook, you will also need to `pip install jupyter` 
