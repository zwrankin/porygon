import pandas as pd
import json
from pathlib import Path

from folium_extensions.data.config import RAW_DATA_DIR
from folium_extensions.h3 import lat_lng_to_h3

def load_chicago_traffic_accidents():
    crashes = pd.read_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_crashes.csv'))
    vehicles = pd.read_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_vehicles.csv'))
    df = pd.merge(crashes, vehicles)  # TODO - specify columns to merge on, and deal with overlap
    df['date_time'] = pd.to_datetime(df.crash_date)
    return df


def load_chicago_traffic_accident_brands_by_h3():
    df = load_chicago_traffic_accidents()
    df['count'] = 1
    vehicle_brand_dummies = pd.get_dummies(df.make)
    vehicle_brands_top = df.make.value_counts()[:21].index.tolist()
    vehicle_brands_top.remove('UNKNOWN')
    df_brands = pd.concat([df[['latitude', 'longitude', 'count']], vehicle_brand_dummies[vehicle_brands_top]], axis=1)
    df_brands['h3'] = df_brands.apply(lambda row: lat_lng_to_h3(row, h3_level=8), axis=1)
    df_h3 = pd.DataFrame(df_brands.groupby('h3')[['count'] + vehicle_brands_top].sum())

    return df_h3


def load_chicago_census_tract_boundaries():
    with open(Path(RAW_DATA_DIR, 'chicago_census_tract_boundaries.json')) as f:
        data = json.load(f)
    return data
