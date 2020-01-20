porygon
==============================
<img src="gallery/porygon.png" alt="drawing" width="120"/>

A library for making beautiful maps from geospatial data.  
- Internally coherent data structures that connect the data manipulation of [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) & [`geopandas.GeoDataFrame`](http://geopandas.org/data_structures.html#geodataframe) with the plotting library [`folium`](https://python-visualization.github.io/folium/). 
- Streamlined aggregation of point data to polygons by providing a consistent interface over geospatial tools such as [`h3`](https://uber.github.io/h3/#/), [`shapely`](https://shapely.readthedocs.io/en/stable/index.html), [`scipy.Voronoi`](https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.spatial.Voronoi.html), and more. 
- First-class plotting methods of `PorygonDataFrame` that streamline data transformations and provide additional plotting utilities (e.g. custom legends) beyond folium. 


## Motivating Example
Using the >200,000 [Chicago Traffic Accidents from 2019](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if), what is the distribution of car brands in different parts of the city in absolute and relative terms? (See [Quickstart](https://github.com/zwrankin/porygon/blob/master/notebooks/Quickstart.ipynb) for analysis code, and [Gallery](https://github.com/zwrankin/porygon/tree/master/gallery) for interactive html and more examples)  

![Accidents by Make](gallery/accidents_by_make_censustract_categorical.png?raw=true "Accidents by Make")
![Accidents by Make](gallery/accidents_by_make_h3_categorical.png?raw=true "Accidents by Make")

## Getting started
Until more formal documentation is available, start by reading the [Quickstart jupyter notebook](https://github.com/zwrankin/porygon/blob/master/notebooks/Quickstart.ipynb)


## [Gallery](https://github.com/zwrankin/porygon/tree/master/gallery  )
*See gallery for interactive html files, not currently able to render in Github*


## Installation 
`porygon` is not available from [pypi](https://pypi.org/), you must clone and install locally.  
```
conda create -n porygon python=3.7 pip
conda activate porygon
cd porygon && python setup.py develop
```

Installation notes: 
- If you are having trouble with the h3 installation, you may need to manually `pip install cmake`.
- If running notebooks, you will need to `pip install jupyter`. 
- Some notebooks render the maps as pngs using folium's [`_to_png`](https://github.com/python-visualization/folium/blob/master/folium/folium.py#L296) method. You can run the notebooks with those lines commented out (and save the folium maps to html as normal). Or if you'd like to use the inline png rendering, you will need to install `geckodriver`. You can see download it [here](https://github.com/mozilla/geckodriver/releases) or by `brew install geckodriver`. 
- Additional dev requirements are specified in `requirements-dev.txt`. 
