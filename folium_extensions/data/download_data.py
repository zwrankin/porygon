import os
import pandas as pd
from dotenv import find_dotenv, load_dotenv
from pathlib import Path
from sodapy import Socrata

from folium_extensions.data.config import RAW_DATA_DIR

load_dotenv(find_dotenv())

socrata_app_token = os.getenv('socrata_app_token')
socrata_client = Socrata("data.cityofchicago.org", app_token=socrata_app_token, timeout=1000)


def download_chicago_traffic_accidents():
    """Download traffic accident data from https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if"""

    # crashes 
    results = socrata_client.get("85ca-t3if", limit = 500_000)  # as of 11/17/2019 there were 360K rows
    df = pd.DataFrame.from_records(results)
    df.to_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_crashes.csv'), index=False)

    # vehicles
    results = socrata_client.get("68nd-jvt3", limit = 1_000_000) 
    df = pd.DataFrame.from_records(results)
    df.to_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_vehicles.csv'), index=False)

    # people
    results = socrata_client.get("u6pd-qa9d", limit = 1_000_000) 
    df = pd.DataFrame.from_records(results)
    df.to_csv(Path(RAW_DATA_DIR, 'chicago_traffic_crashes_people.csv'), index=False)


if __name__ == "__main__":
    download_chicago_traffic_accidents()
