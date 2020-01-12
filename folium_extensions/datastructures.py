import numpy as np 
import pandas as pd
from geopandas import GeoDataFrame
from geojson import Feature, FeatureCollection
from shapely.geometry import shape, Point, Polygon
from h3 import h3


def _validate_latitude_longitude_columns(df: pd.DataFrame):
    assert all(c in df.columns for c in ['latitude', 'longitude']), 'latitude and longitude not found in columns'


def _lat_lng_to_h3(row, h3_level: int):
    """
    Utility to add h3 column to pd.DataFrame, could likely be turned to a lambda function
    df['h3'] = df.apply(lambda row: lat_lng_to_h3(row, h3_level=8), axis=1)
    """
    return h3.geo_to_h3(row['latitude'], row['longitude'], h3_level)


def _h3_to_polygon(h3_address: str):
    """Wrapper for h3.h3_to_geo_boundary to return shapely.geometry.Polygon"""
    return Polygon(h3.h3_to_geo_boundary(h3_address, geo_json=True)) 


class PolygonDataFrame(GeoDataFrame):
    """
    A PolygonDataFrame extends the functionality of GeoDataFrame objects with regard to polygons 
    """

    def __init__(self, *args, **kwargs):
        super(PolygonDataFrame, self).__init__(*args, **kwargs)
        
    def from_dataframe(self, df):
        assert 'geometry' in df.columns, 'If no geometry passed, PolygonDataFrame functionality wont work - either add geometry or use a child class e.g. H3DataFrame().from_dataframe()'
        return PolygonDataFrame(df) 

    def to_feature_collection(self):
        """
        Wrapper for GeoDataFrame._to_geo() that returns the Python dict as geojson.FeatureCollection
        The features have 'id' fields that correspond to the 'id' index of the PolygonDataFrame.to_feature_dataframe
        """
        # NOTE - watch out for issues with non-numeric ids, I've seen folium reject them in choropleth. I think the dtypes between geojson 'id' and 'id' col need to match 
        fc  = FeatureCollection([Feature(id = f['properties']['id'], geometry=f['geometry']) for f in self._to_geo()['features']])
        return fc

    def to_feature_dataframe(self):
        """Returns a pd.DataFrame with 'id' index that corresponds to the FeatureCollection ids of PolygonDataFrame.to_feature_collection()"""
        df = pd.DataFrame(self.drop(columns='geometry').set_index('id'))
        return df
    
    
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
        df : pd.DataFrame of lat/long data to be aggregated
        aggfunc : function or string used to aggregate to h3 tile
            For now, all columns will get aggregated with the same aggfunc

        Returns
        -------
        h3df  : H3DataFrame of the dataframe aggregated to h3 tiles
        """
        _validate_latitude_longitude_columns(df)
        df.dropna(subset=['latitude', 'longitude'], inplace=True)
        df['id'] = df.apply(_lat_lng_to_h3, args=(h3_level, ), axis=1)
        df = df.drop(columns=['latitude', 'longitude'])
        df = df.groupby('id').apply(aggfunc)  
        # Ugh - some functions (e.g. np.sum) keep the groupby col ('id'), others (e.g. np.mean) remove it
        if 'id' in df.columns: 
            df = df.drop(columns='id').reset_index()
        else: 
            df = df.reset_index()
        df['geometry'] = df.id.apply(_h3_to_polygon)
        return H3DataFrame(df) 
