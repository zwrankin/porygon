import pandas as pd
from h3 import h3
from branca.element import Template, MacroElement


def lat_lng_to_h3(row, h3_level=9):
    """
    Utility to add h3 column to pd.DataFrame
    df['h3'] = df.apply(lambda row: lat_lng_to_h3(row, h3_level=8), axis=1)
    """
    return h3.geo_to_h3(row['latitude'], row['longitude'], h3_level)


# def make_h3_df(df, var=None, h3_level=9):
#     """A half-baked function to aggregate dataframes by h3 tile"""
#     if var is None:
#         var = 'count'
#         df[var] = 1
#     df['h3'] = df.apply(lambda row: lat_lng_to_h3(row, h3_level=h3_level), axis=1)
#     df_h3 = df.groupby('h3')[var].sum().reset_index()
#     return df_h3


def h3df_to_geojson(df: pd.DataFrame):
    """
    Convert pd.DataFrame to geojson object. By default will turn all columns into properties
    TODO - need to handle dtypes in json serialization - check for int32 or int64
    """
    if df.index.name == 'h3':
        df = df.reset_index()
    assert 'h3' in df.columns

    h3_to_feature = lambda row: {
      "type": "Feature",
        'id': row['h3'],
      "geometry": {
        "type": "Polygon",
        "coordinates": [h3.h3_to_geo_boundary(row['h3'], geo_json=True)]
      },
      "properties": dict(row) 
    }
    
    features = [h3_to_feature(row) for index, row in df.reset_index().iterrows()]
    return {"type":"FeatureCollection","features": features}


def make_h3_legend_html(color_key: dict, title='Legend (draggable!)'):
    """
    Generate html needed for color-coded hexagons  
    Adapted from https://nbviewer.jupyter.org/gist/talbertc-usgs/18f8901fc98f109f2b71156cf3ac81cd
        :param color_key: dictionary with keys of the categories, and values of valid folium color codes
    """
    # Ordered list of legend elements
    labels = ''
    for key, color in color_key.items():
        labels += f"""<li><span style="color: {color};">&#x2B22;</span>{key}</li>"""
    template = """
        {% macro html(this, kwargs) %}

        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>jQuery UI Draggable - Default functionality</title>
          <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

          <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
          <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

          <script>
          $( function() {
            $( "#maplegend" ).draggable({
                            start: function (event, ui) {
                                $(this).css({
                                    right: "auto",
                                    top: "auto",
                                    bottom: "auto"
                                });
                            }
                        });
        });

          </script>
        </head>
        <body>


        <div id='maplegend' class='maplegend' 
            style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
             border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>

        <div class='legend-title'>""" + title + """</div>
        <div class='legend-scale'>
          <ul class='legend-labels'>
          """ + labels + """
          </ul>
        </div>
        </div>

        </body>
        </html>

        <style type='text/css'>
          .maplegend .legend-title {
            text-align: left;
            margin-bottom: 5px;
            font-weight: bold;
            font-size: 90%;
            }
          .maplegend .legend-scale ul {
            margin: 0;
            margin-bottom: 5px;
            padding: 0;
            float: left;
            list-style: none;
            }
          .maplegend .legend-scale ul li {
            font-size: 80%;
            list-style: none;
            margin-left: 0;
            line-height: 22px;
            margin-bottom: 2px;
            }
          .maplegend ul.legend-labels li span {
            float: left;
            width: 25x;
            margin-right: 5px;
            margin-left: 0;
            font-size: 25px;
            opacity: 0.8;
            }
          .maplegend .legend-source {
            font-size: 80%;
            color: #777;
            clear: both;
            }
          .maplegend a {
            color: #777;
            }
        </style>
        {% endmacro %}"""

    return template 


def add_h3_legend(m, color_key:dict, title='Legend (draggable!)'):
    macro = MacroElement()
    macro._template = Template(make_h3_legend_html(color_key, title=title))
    m.get_root().add_child(macro)
    return m
