import pandas as pd
import numpy as np
from pathlib import Path

from porygon import PorygonDataFrame
from porygon.data.config import PROCESSED_DATA_DIR


def test_porygondataframe_from_h3():
    df = pd.read_csv(Path(PROCESSED_DATA_DIR, 'chicago_traffic_accidents.csv'), nrows=1000)
    df['count'] = 1
    h3df = PorygonDataFrame().from_h3(df[['latitude', 'longitude', 'count']], h3_level=8, aggfunc=np.sum)
    h3df['category'] = np.random.choice(['a', 'b', 'c'], len(h3df))
    m = h3df.to_choropleth('count')
    m = h3df.to_categorical_map('count', 'category')
