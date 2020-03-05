import pandas as pd
import numpy as np
from pathlib import Path
from shapely.geometry import shape, Point, Polygon, MultiPolygon, MultiPoint
from geopandas import GeoDataFrame
import pytest

from porygon import PorygonDataFrame
from porygon.utils.data import df_to_gpdf, _validate_point_data
from porygon.data import load_chicago_census_tract_boundaries, load_chicago_L_stops

from porygon.data import PROCESSED_DATA_DIR


def test_porygondataframe_from_h3():
    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv.gz'), nrows=1000, compression='gzip')
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

    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv.gz'), nrows=1000, compression='gzip')
    df['count'] = 1
    cdf = PorygonDataFrame().from_boundaries(df[['latitude', 'longitude', 'count']], gpdf_census)
    cdf['category'] = np.random.choice(['a', 'b', 'c'], len(cdf))

    m = cdf.to_choropleth('count')
    m = cdf.to_categorical_map('count', 'category')


def test_porygondataframe_from_voronoi():
    df_stops = load_chicago_L_stops()
    df_stops.index.name = 'id'
    gpdf = df_to_gpdf(df_stops)

    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv.gz'), nrows=1000, compression='gzip')
    df['count'] = 1
    
    pdf = PorygonDataFrame().from_voronoi(df[['latitude', 'longitude', 'count']], gpdf)
    pdf['category'] = np.random.choice(['a', 'b', 'c'], len(pdf))

    m = pdf.to_choropleth('count')
    m = pdf.to_categorical_map('count', 'category')


def test_porygon_index():
    census_tracts = load_chicago_census_tract_boundaries()
    boundaries = [shape(tract['the_geom']) for tract in census_tracts]
    ids = [tract['geoid10'] for tract in census_tracts]
    names = [tract['namelsad10'] for tract in census_tracts]
    int_index = [i for i in range(0, len(census_tracts))]
    dup_names =['dupe_name' for i in range(0, len(census_tracts))] 
    gpdf = GeoDataFrame({'geometry': boundaries, 'id': ids, 'census_name': names, 
                         'dupe_index': dup_names, 'int_index': int_index})
    
    with pytest.raises(AssertionError):
        pgdf = PorygonDataFrame(gpdf.set_index('dupe_index'))

    with pytest.raises(AssertionError):
        pgdf = PorygonDataFrame(gpdf.set_index(['int_index', 'census_name']))

    with pytest.warns(Warning):
        pgdf = PorygonDataFrame(gpdf.set_index(['int_index']))

def test_porygon_geometry():
    gpdf = GeoDataFrame({'geometry': [Point(0,0)]})
    with pytest.raises(AssertionError):
        pgdf = PorygonDataFrame(gpdf)

    # should be able to handle mixed shapes
    box1 = [(0,0), (0,1), (1,1), (1,0)]
    box2 = [(2,2), (2,3), (3,3), (3,2)]
    gpdf = GeoDataFrame({'geometry': [Polygon(box1), MultiPolygon([Polygon(box1), Polygon(box2)])]})
    pgdf = PorygonDataFrame(gpdf)

def test_point_geometry():
    p1 = (0,0)
    p2 = (1,1)
    gpdf = GeoDataFrame({'geometry': [MultiPoint([p1,p2])]})
    with pytest.raises(AssertionError):
        _validate_point_data(GeoDataFrame({'geometry': [MultiPoint([p1,p2])]}))
