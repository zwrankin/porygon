import os
from pathlib import Path
RAW_DATA_DIR = Path(Path(os.path.dirname(__file__)).parent.parent, 'data/raw')
PROCESSED_DATA_DIR = Path(Path(os.path.dirname(__file__)), 'datasets')
from porygon.data.load_data import load_chicago_traffic_accidents, load_chicago_census_tract_boundaries, load_chicago_L_stops, load_air_quality_data
