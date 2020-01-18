import pandas as pd
import json
from pathlib import Path
import ast 

from porygon.data.config import RAW_DATA_DIR, PROCESSED_DATA_DIR


def process_chicago_traffic_accidents():
    crashes = pd.read_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_crashes.csv'))
    vehicles = pd.read_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_vehicles.csv'))
    df = pd.merge(crashes, vehicles)  # TODO - specify columns to merge on, and deal with overlap
    df['date_time'] = pd.to_datetime(df.crash_date)
    df = df.loc[df['date_time'].dt.year == 2019]
    df['crash_date'] = df['date_time'].dt.strftime('%Y-%m-%d')
    cols = ['rd_no', 'crash_date', 'latitude', 'longitude', 'unit_type', 'make']
    df = df[cols]
    df.to_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv'), index=False)


def process_chicago_L_stops():
    df = pd.read_csv(Path(RAW_DATA_DIR, 'chicago_L_stops.csv'))
    df = df.drop_duplicates('map_id')  # don't need separate N/S and E/W stops
    df['latitude'] = df.location.apply(lambda x: float(ast.literal_eval(x)['latitude'])) 
    df['longitude'] = df.location.apply(lambda x: float(ast.literal_eval(x)['longitude'])) 
    cols = ['station_name', 'latitude', 'longitude', 'station_descriptive_name',  'red', 'blue', 'g', 'brn', 'p', 'pexp', 'y', 'pnk', 'o']
    df = df[cols]
    df.to_csv(Path(PROCESSED_DATA_DIR, 'chicago_L_stops.csv'), index=False)

if __name__ == "__main__":
    process_chicago_traffic_accidents()
    process_chicago_L_stops()
