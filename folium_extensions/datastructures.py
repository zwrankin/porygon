import numpy as np 
import pandas as pd
import geopandas
from geopandas import GeoDataFrame, GeoSeries
from geojson import Feature, FeatureCollection
from shapely.geometry import shape, Point, Polygon
from h3 import h3
import folium
import seaborn as sns
from pandas.api.types import is_string_dtype, is_numeric_dtype

from folium_extensions.plotting import add_h3_legend

class PolygonDataFrame(GeoDataFrame):
    """
    A PolygonDataFrame extends the functionality of GeoDataFrame objects with regard to polygons 
    Can be constructed from polygon-indexed data using from_gpdf or from point data using various constructor methods such as from_h3
    that aggregate the point data to corresponding polygons. 
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self) > 0:  # if initialized from a constructor, not PolygonDataFrame()
            centroids = self.centroid
            self.centroid_point = [centroids.y.mean(), centroids.x.mean()]  # don't want to overwrite self.centroid attribute
            # Rough logic - seems to work for Chicago but TBD if generalizes at higher/lower scales
            self.zoom = round(max(centroids.x.quantile(0.95) - centroids.x.quantile(0.05), centroids.y.quantile(0.95) - centroids.y.quantile(0.05)) * 40)
            # self.map = self._make_base_map()  # may be used later to allowing layering

    def from_gpdf(self, gpdf):
        # TODO - validate that geometry is polygon 
        # TODO - isn't this constructor superfluous, given that it functions the same as __init___ ? Dunno if this explicit constructor is helpful or confusing
        assert isinstance(gpdf, GeoDataFrame)
        return PolygonDataFrame(df) 

    def from_h3(self, df, h3_level=9, aggfunc=np.sum):
        return _df_to_h3(df, h3_level=9, aggfunc=np.sum)

    def from_boundaries(self, df: pd.DataFrame, boundaries: GeoDataFrame, aggfunc=np.sum):
        return _df_to_boundaries(df, boundaries, aggfunc)

    def to_feature_collection(self):
        """
        Wrapper for GeoDataFrame._to_geo() that returns the Python dict as geojson.FeatureCollection
        The features 'id' values correspond to the 'id' index of the PolygonDataFrame, which is helpful for plotting utilities
        """
        # NOTE - watch out for issues with non-numeric ids, I've seen folium reject them in choropleth. I think the dtypes between geojson 'id' and 'id' col need to match 
        fc  = FeatureCollection([Feature(id = f['id'], geometry=f['geometry'], properties=f['properties']) for f in self._to_geo()['features']])
        return fc

    def _make_base_map(self):
        # TODO - should be class attribute 
        return folium.Map(location=self.centroid_point, zoom_start=self.zoom) 

    def to_choropleth(self, col: str, m=None, fill_color='YlOrRd', **kwargs):
        """
        Make folium.Choropleth map
        To add a layer to existing map, provide an instance of folium.Map
        ----------
        col : Name of column in dataframe to plot
        m : folium.Map object. If not provided, makes a new map with just the choropleth layer
        Returns
        -------
        folium.Map with added Choropleth layer 
        """
        assert col in self.columns, f"col {col} not found in dataframe columns - {self.columns.tolist()}"

        # TODO - allow layering to self.map 
        if m is None:
            m = self._make_base_map()

        folium.Choropleth(
            geo_data=self.to_feature_collection(),
            name='choropleth',
            data=self.reset_index(), 
            columns=['id', col],
            key_on='feature.id',
            fill_color=fill_color,
            **kwargs
        ).add_to(m)

        return m

    def to_categorical_map(self, val_col: str, cat_col: str, m=None, color_key=None, nan_fill_color='black', **kwargs):
        """
        Make custom folium.GeoJson with categorical observations 
        To add a layer to existing map, provide an instance of folium.Map
        ----------
        val_col : Name of column with values 
        cat_col : Name of column with categorical values 
        m : folium.Map object. If not provided, makes a new map with just the categorical map layer
        Returns
        -------
        folium.Map with added layer 
        """
        # TODO - refactor this elsewhere
        assert val_col in self.columns, f"val_col {val_col} not found in dataframe columns - {self.columns.tolist()}"
        assert cat_col in self.columns, f"cat_col {cat_col} not found in dataframe columns - {self.columns.tolist()}"
        assert is_numeric_dtype(self[val_col]), f'{val_col} is not numeric'
        assert is_string_dtype(self[cat_col]), f'{cat_col} is not numeric'

        if color_key is None: 
            categories = self[cat_col].value_counts().index  # default is sort by frequency
            colors = sns.color_palette('deep', 10).as_hex() + sns.color_palette('bright', 10).as_hex()

            if len(categories) > len(colors):
                # TODO - log a warning that can only take top n colors
                color_key = dict(zip(categories[:len(colors)], colors))
            else: 
                color_key = dict(zip(categories, colors[:len(categories)]))

        # TODO - allow layering to self.map 
        if m is None:
            m = self._make_base_map()

        def style_function(feature):
            row = self.loc[feature['id']]
            if row[cat_col] in color_key.keys():
                color = color_key[row[cat_col]] 
            else: 
                color = nan_fill_color 
            opacity = 0.7 
            return {
                'weight': 2,
                'opacity': opacity,
                'color': color,
                'fillColor': color,
                'fillOpacity': opacity, 
            }

        folium.GeoJson(
            self.to_feature_collection(),
            style_function=style_function,
            tooltip=folium.features.GeoJsonTooltip(
                fields=[cat_col, val_col],
                # aliases=['Category', 'Value'],
            ),
            **kwargs
        ).add_to(m)

        m = add_h3_legend(m, color_key)

        return m


def _df_to_boundaries(df: pd.DataFrame, boundaries: GeoDataFrame, aggfunc=np.sum):
    """
    Aggreggates point data to the corresponding polygon boundaries 
    TODO - make more flexible in terms of boundaries.index allowed
    Parameters
    ----------
    df : pd.DataFrame of lat/long data to be aggregated, or GeoDataFrame with valid point geometry
    boundaries : GeoSeries of polygon geometry
    aggfunc : function or string used to aggregate to polygon
        For now, all columns will get aggregated with the same aggfunc

    Returns
    -------
    PolygonDataFrame of the dataframe aggregated to polygon, with index 'id' of the boundaries's 'id' index
    """

    assert boundaries.index.name == 'id'
    df = _validate_point_data(df)

    if not isinstance(df, GeoDataFrame):
        df = _df_to_gpdf(df)
    
    if isinstance(boundaries, GeoSeries):
        srs = boundaries.copy()
    else: 
        srs = boundaries['geometry']

    df = _assign_polygon_index(df, srs)

    df = df.drop(columns='geometry').groupby('id').apply(aggfunc)
    # Ugh - some functions (e.g. np.sum) keep the groupby col ('id'), others (e.g. np.mean) remove it
    if 'id' in df.columns: 
        df = df.drop(columns='id').reset_index()
    else: 
        df = df.reset_index()
    
    gpdf = pd.merge(df.reset_index(), boundaries, on='id') 
    
    return PolygonDataFrame(gpdf.set_index('id')) 
    

def _df_to_h3(df, h3_level=8, aggfunc=np.sum):
    """
    Aggregates point data to corresponding h3 polygons 
    For more on h3 see https://uber.github.io/h3/#/
    Parameters
    ----------
    df : pd.DataFrame of lat/long data to be aggregated, or GeoDataFrame with valid point geometry
    h3_level : resolution of h3_tiles. Default is arbitrary
    aggfunc : function or string used to aggregate to h3 tile
        For now, all columns will get aggregated with the same aggfunc

    Returns
    -------
    H3DataFrame of the dataframe aggregated to h3 tiles, with index 'id' of h3 tile code
    """
    df = _validate_point_data(df)

    if isinstance(df, GeoDataFrame):
        df = _gpdf_to_latlong_df(df)

    # Utility for h3.geo_to_h3 to work on dataframe row
    lat_lng_to_h3 = lambda row, h3_level: h3.geo_to_h3(row['latitude'], row['longitude'], h3_level)
    df['id'] = df.apply(lat_lng_to_h3, args=(h3_level, ), axis=1)

    df = df.drop(columns=['latitude', 'longitude'])
    df = df.groupby('id').apply(aggfunc)  
    # Ugh - some functions (e.g. np.sum) keep the groupby col ('id'), others (e.g. np.mean) remove it
    if 'id' in df.columns: 
        df = df.drop(columns='id').reset_index()
    else: 
        df = df.reset_index()
    
    # Utilty for for h3.h3_to_geo_boundary to return shapely.geometry.Polygon
    h3_to_polygon = lambda h3_address: Polygon(h3.h3_to_geo_boundary(h3_address, geo_json=True)) 
    df['geometry'] = df.id.apply(h3_to_polygon)
    
    return PolygonDataFrame(df.set_index('id')) 


def _validate_point_data(df: pd.DataFrame):
    """
    Validates that data has valid point data, removes missingness. 
    Parameters
    ----------
    df : pd.DataFrame with latitude & longitude columns, or GeoDataFrame with valid point geometry
    """
    if isinstance(df, GeoDataFrame):
        # TODO - validate that index contains alls points (not polygons)
        print('using unvalidated GeoDataFrame')
    elif isinstance(df, pd.DataFrame): 
        assert all(c in df.columns for c in ['latitude', 'longitude']), 'latitude and longitude not found in columns'
        # TODO - throw warning if any missingness
        df.dropna(subset=['latitude', 'longitude'], inplace=True)
    else: 
        raise ValueError(f'Data structure not recognized: {type(df)}')

    return df


def _gpdf_to_latlong_df(gpdf: GeoDataFrame):
    """Converts GeoDataFrame with point geometry to pd.DataFrame with latitude and longitude columns"""
    gpdf['longitude'] = gpdf.geometry.x
    gpdf['latitude'] = gpdf.geometry.y
    return gpdf.drop(columns='geometry')


def _df_to_gpdf(df: pd.DataFrame):
    """Converts pd.DataFrame with latitude and longitude columns to GeoDataFrame with point geometry"""
    return GeoDataFrame(df.drop(columns=['latitude', 'longitude']), geometry=geopandas.points_from_xy(df.longitude, df.latitude))


def _assign_polygon_index(gpdf: GeoDataFrame, polygons: GeoSeries):
    """
    Given a gpdf with point geometry, add a 'id' column of the index value of the polygon containing the point.
    Not giving the gpdf a polygon geoseries index directly due to size concerns, and allow different aggregations. 
    Parameters
    ----------
    gpdf : GeoDataFrame with point geometry 
    polygons : GeoSeries of polygon geometry

    Returns
    -------
    gpdf  : GeoDataFrame with additional column 'id' which corresponds to the index of the polygon containing the point geometry
    """

    for i in polygons.index:
        gpdf.loc[gpdf.geometry.within(polygons.loc[i]), 'id'] = i
   
    return gpdf
