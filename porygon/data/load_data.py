import pandas as pd
import json
from pathlib import Path

from porygon.data.config import PROCESSED_DATA_DIR


def load_chicago_traffic_accidents():
    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv'))
    return df


def load_chicago_census_tract_boundaries():
    with open(Path(PROCESSED_DATA_DIR, 'chicago_census_tract_boundaries.json')) as f:
        data = json.load(f)
    return data


def load_chicago_L_stops():
    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'chicago_L_stops.csv'))
    return df


def load_air_quality_data():
    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'air_quality_data.csv'))
    return df
