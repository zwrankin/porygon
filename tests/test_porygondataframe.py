import pandas as pd
import numpy as np
from pathlib import Path
from shapely.geometry import shape
from geopandas import GeoDataFrame

from porygon import PorygonDataFrame
from porygon.utils.data import df_to_gpdf
from porygon.data.config import PROCESSED_DATA_DIR
from porygon.data import load_chicago_census_tract_boundaries, load_chicago_L_stops


def test_porygondataframe_from_h3():
    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv'), nrows=1000)
    df['count'] = 1
    h3df = PorygonDataFrame().from_h3(df[['latitude', 'longitude', 'count']], h3_level=8, aggfunc=np.sum)
    h3df['category'] = np.random.choice(['a', 'b', 'c'], len(h3df))
    m = h3df.to_choropleth('count')
    m = h3df.to_categorical_map('count', 'category')


def test_porygondataframe_from_boundaries():
    census_tracts = load_chicago_census_tract_boundaries()
    boundaries = [shape(tract['the_geom']) for tract in census_tracts]
    ids = [tract['geoid10'] for tract in census_tracts]
    names = [tract['namelsad10'] for tract in census_tracts]
    gpdf_census = GeoDataFrame({'geometry': boundaries, 'id': ids, 'census_name': names}).set_index('id')

    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv'), nrows=1000)
    df['count'] = 1
    cdf = PorygonDataFrame().from_boundaries(df[['latitude', 'longitude', 'count']], gpdf_census)
    cdf['category'] = np.random.choice(['a', 'b', 'c'], len(cdf))

    m = cdf.to_choropleth('count')
    m = cdf.to_categorical_map('count', 'category')


def test_porygondataframe_from_voronoi():
    df_stops = load_chicago_L_stops()
    df_stops.index.name = 'id'
    gpdf = df_to_gpdf(df_stops)

    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv'), nrows=1000)
    df['count'] = 1
    
    pdf = PorygonDataFrame().from_voronoi(df[['latitude', 'longitude', 'count']], gpdf)
    pdf['category'] = np.random.choice(['a', 'b', 'c'], len(pdf))

    m = pdf.to_choropleth('count')
    m = pdf.to_categorical_map('count', 'category')
