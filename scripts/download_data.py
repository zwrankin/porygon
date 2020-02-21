import os
import pandas as pd
import requests
import zipfile
import io
import json
from dotenv import find_dotenv, load_dotenv
from pathlib import Path
from sodapy import Socrata

from porygon.data import RAW_DATA_DIR, PROCESSED_DATA_DIR

load_dotenv(find_dotenv())

socrata_app_token = os.getenv('socrata_app_token')
socrata_client = Socrata("data.cityofchicago.org", app_token=socrata_app_token, timeout=1000)


def download_chicago_traffic_accidents():
    """Download traffic accident data from https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if"""

    # crashes 
    results = socrata_client.get("85ca-t3if", limit = 500_000)  # as of 11/17/2019 there were 360K rows
    df = pd.DataFrame.from_records(results)
    df.to_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_crashes.csv.gz'), index=False, compression='gzip')

    # vehicles
    results = socrata_client.get("68nd-jvt3", limit = 1_000_000) 
    df = pd.DataFrame.from_records(results)
    df.to_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_vehicles.csv.gz'), index=False, compression='gzip')

    # people
    results = socrata_client.get("u6pd-qa9d", limit = 1_000_000) 
    df = pd.DataFrame.from_records(results)
    df.to_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_people.csv.gz'), index=False, compression='gzip')


def download_chicago_census_tract_boundaries():
    """Download census tract shapefiles from https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Census-Tracts-2010/5jrd-6zik"""
    results = socrata_client.get("74p9-q2aq", limit = 1_000_000) 
    with open(Path(RAW_DATA_DIR, 'chicago_census_tract_boundaries.json'), 'w') as f:
        json.dump(results, f)
    # Since there are no changes, just directly save in processed data
    with open(Path(PROCESSED_DATA_DIR, 'chicago_census_tract_boundaries.json'), 'w') as f:
        json.dump(results, f)


def download_chicago_cta_L_stops():
    """Download Chicago CTA L stops from https://data.cityofchicago.org/Transportation/CTA-System-Information-List-of-L-Stops/8pix-ypme"""
    results = socrata_client.get("8pix-ypme", limit = 1_000_000) 
    df = pd.DataFrame.from_records(results)
    df.to_csv(Path(RAW_DATA_DIR, 'chicago_L_stops.csv.gz'), index=False, compression='gzip')
    

def download_annual_conc_by_monitor_2019():
    """Download USA air quality data from https://aqs.epa.gov/aqsweb/airdata/download_files.html"""
    r = requests.get('https://aqs.epa.gov/aqsweb/airdata/annual_conc_by_monitor_2019.zip')
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(RAW_DATA_DIR)


if __name__ == "__main__":
    download_chicago_traffic_accidents()
    download_chicago_census_tract_boundaries()
    download_chicago_cta_L_stops()
    download_annual_conc_by_monitor_2019()
