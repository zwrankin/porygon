import pandas as pd
import json
from pathlib import Path
import ast 
import os

from porygon.data import RAW_DATA_DIR, PROCESSED_DATA_DIR
# RAW_DATA_DIR = Path(Path(os.path.dirname(__file__)).parent, 'data/raw')
# PROCESSED_DATA_DIR = Path(Path(os.path.dirname(__file__)).parent, 'porygon/data/datasets')


def process_chicago_traffic_accidents():
    crashes = pd.read_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_crashes.csv.gz'), compression='gzip')
    vehicles = pd.read_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_vehicles.csv.gz'), compression='gzip')
    df = pd.merge(crashes, vehicles)  # TODO - specify columns to merge on, and deal with overlap
    df['date_time'] = pd.to_datetime(df.crash_date)
    df = df.loc[df['date_time'].dt.year == 2019]
    df['crash_date'] = df['date_time'].dt.strftime('%Y-%m-%d')
    cols = ['rd_no', 'crash_date', 'latitude', 'longitude', 'unit_type', 'make']
    df = df[cols]
    df.to_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv.gz'), index=False, compression='gzip')


def process_chicago_L_stops():
    df = pd.read_csv(Path(RAW_DATA_DIR, 'chicago_L_stops.csv.gz'), compression='gzip')
    df = df.drop_duplicates('map_id')  # don't need separate N/S and E/W stops
    df['latitude'] = df.location.apply(lambda x: float(ast.literal_eval(x)['latitude'])) 
    df['longitude'] = df.location.apply(lambda x: float(ast.literal_eval(x)['longitude'])) 
    cols = ['station_name', 'latitude', 'longitude', 'station_descriptive_name',  'red', 'blue', 'g', 'brn', 'p', 'pexp', 'y', 'pnk', 'o']
    df = df[cols]
    df.to_csv(Path(PROCESSED_DATA_DIR, 'chicago_L_stops.csv.gz'), index=False, compression='gzip')


def process_air_quality_data():
    df = pd.read_csv(Path(RAW_DATA_DIR, 'annual_conc_by_monitor_2019.csv'))
    rename_dict = {'Latitude': 'latitude', 
               'Longitude': 'longitude', 
               'Year': 'year',
               'Local Site Name': 'site_name', 
               'Parameter Name': 'parameter',
               'Arithmetic Mean': 'val_mean'}

    df = df.rename(columns=rename_dict)
    df = df.loc[df['Sample Duration'] == "24 HOUR"]
    df['site_code'] = df['State Code'].astype('str') + df['County Code'].astype('str') + df['Site Num'].astype('str')
    df.drop_duplicates(subset=['site_code', 'parameter'], inplace=True)

    cols = ['site_code', 'latitude', 'longitude', 'year', 'parameter', 'val_mean']
    df = df[cols]
    df.to_csv(Path(PROCESSED_DATA_DIR, 'air_quality_data.csv.gz'), index=False, compression='gzip')


if __name__ == "__main__":
    process_chicago_traffic_accidents()
    process_chicago_L_stops()
    process_air_quality_data()
