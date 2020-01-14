import numpy as np 
import pandas as pd
import geopandas
from geopandas import GeoDataFrame, GeoSeries
from geojson import Feature, FeatureCollection
from shapely.geometry import shape, Point, Polygon
from h3 import h3


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


def _lat_lng_to_h3(row, h3_level: int):
    """
    Utility to add h3 column to pd.DataFrame, could likely be turned to a lambda function
    df['h3'] = df.apply(lambda row: lat_lng_to_h3(row, h3_level=8), axis=1)
    """
    return h3.geo_to_h3(row['latitude'], row['longitude'], h3_level)


def _h3_to_polygon(h3_address: str):
    """Wrapper for h3.h3_to_geo_boundary to return shapely.geometry.Polygon"""
    return Polygon(h3.h3_to_geo_boundary(h3_address, geo_json=True)) 


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


class PolygonDataFrame(GeoDataFrame):
    """
    A PolygonDataFrame extends the functionality of GeoDataFrame objects with regard to polygons 
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def from_dataframe(self, df):
        assert 'geometry' in df.columns, 'If no geometry passed, PolygonDataFrame functionality wont work - either add geometry or use a child class e.g. H3DataFrame().from_dataframe()'
        return PolygonDataFrame(df) 

    def to_feature_collection(self):
        """
        Wrapper for GeoDataFrame._to_geo() that returns the Python dict as geojson.FeatureCollection
        The features have 'id' fields that correspond to the 'id' index of the PolygonDataFrame.to_feature_dataframe
        """
        # NOTE - watch out for issues with non-numeric ids, I've seen folium reject them in choropleth. I think the dtypes between geojson 'id' and 'id' col need to match 
        fc  = FeatureCollection([Feature(id = f['id'], geometry=f['geometry'], properties=f['properties']) for f in self._to_geo()['features']])
        return fc

    # DEPRECATED - the index should already be 'id'. Since it inherits from pd.DataFrame all functionality should exist in self 
    # def to_feature_dataframe(self):
    #     """Returns a pd.DataFrame with 'id' index that corresponds to the FeatureCollection ids of PolygonDataFrame.to_feature_collection()"""
    #     df = pd.DataFrame(self.drop(columns='geometry').set_index('id'))
    #     return df
    


class AdminDataFrame(PolygonDataFrame):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
    
    def from_dataframe(self, df: pd.DataFrame, boundaries: GeoDataFrame, aggfunc=np.sum):
        """
        Initialize the AdminDataFrame with point data and the corresponding polygon boundaries 
        TODO - make more flexible in terms of boundaries.index allowed
        Parameters
        ----------
        df : pd.DataFrame of lat/long data to be aggregated, or GeoDataFrame with valid point geometry
        aggfunc : function or string used to aggregate to polygon
            For now, all columns will get aggregated with the same aggfunc

        Returns
        -------
        AdminDataFrame of the dataframe aggregated to polygon
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
        
        return AdminDataFrame(gpdf.set_index('id')) 
    

class H3DataFrame(PolygonDataFrame):

    """
    H3 implementation for PolygonDataFrame. Aggregate point observations to h3 tiles. 
    For more on h3 see https://uber.github.io/h3/#/
    For now must be initialized with H3DataFrame().from_dataframe()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def from_dataframe(self, df, h3_level=9, aggfunc=np.sum):
        """
        Initialize the H3DataFrame with data 
        Parameters
        ----------
        df : pd.DataFrame of lat/long data to be aggregated, or GeoDataFrame with valid point geometry
        aggfunc : function or string used to aggregate to h3 tile
            For now, all columns will get aggregated with the same aggfunc

        Returns
        -------
        H3DataFrame of the dataframe aggregated to h3 tiles
        """
        df = _validate_point_data(df)

        if isinstance(df, GeoDataFrame):
            df = _gpdf_to_latlong_df(df)

        df['id'] = df.apply(_lat_lng_to_h3, args=(h3_level, ), axis=1)
        df = df.drop(columns=['latitude', 'longitude'])
        df = df.groupby('id').apply(aggfunc)  
        # Ugh - some functions (e.g. np.sum) keep the groupby col ('id'), others (e.g. np.mean) remove it
        if 'id' in df.columns: 
            df = df.drop(columns='id').reset_index()
        else: 
            df = df.reset_index()
        df['geometry'] = df.id.apply(_h3_to_polygon)
        return H3DataFrame(df.set_index('id')) 
