import pandas as pd
import geopandas
from geopandas import GeoDataFrame

def _validate_point_data(df: pd.DataFrame):
    """
    Validates that data has valid point data, removes missingness. 
    Parameters
    ----------
    df : pd.DataFrame with latitude & longitude columns, or GeoDataFrame with valid point geometry
    """
    if isinstance(df, GeoDataFrame):
        assert all(df.geometry.geom_type == "Point"), f'Only Point Data supported - data contains {df.geometry.type.unique().tolist()}'
    elif isinstance(df, pd.DataFrame): 
        assert all(c in df.columns for c in ['latitude', 'longitude']), 'latitude and longitude not found in columns'
        # TODO - throw warning if any missingness
        df.dropna(subset=['latitude', 'longitude'], inplace=True)
    else: 
        raise ValueError(f'Data structure not recognized: {type(df)}')

    return df


def gpdf_to_latlong_df(gpdf: GeoDataFrame):
    """Converts GeoDataFrame with point geometry to pd.DataFrame with latitude and longitude columns"""
    gpdf['longitude'] = gpdf.geometry.x
    gpdf['latitude'] = gpdf.geometry.y
    return gpdf.drop(columns='geometry')


def df_to_gpdf(df: pd.DataFrame):
    """Converts pd.DataFrame with latitude and longitude columns to GeoDataFrame with point geometry"""
    return GeoDataFrame(df.drop(columns=['latitude', 'longitude']), geometry=geopandas.points_from_xy(df.longitude, df.latitude))

