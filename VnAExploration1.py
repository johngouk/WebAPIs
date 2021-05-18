import requests
#from ivpy import attach,show,compose,montage,histogram,scatter
import pandas as pd
import altair as alt
#req = pd.read_csv('https://api.vam.ac.uk/v2/objects/search?id_place=x28816&year_made_from=1865&year_made_to=1880&images_exist=1&response_format=csv&page_size=50')
#req.head()

rawData = requests.get('https://api.vam.ac.uk/v2/objects/clusters/object_type/search?id_place=x28816&year_made_from=1865&year_made_to=1880&cluster_size=100')

data = rawData.json();

object_types_df = pd.DataFrame(data);

bars = alt.Chart(object_types_df).mark_bar().encode(
    x='count:Q',
    y="value:O"
)

text = bars.mark_text(
    align='left',
    baseline='middle',
    dx=3  # Nudges text to right so it doesn't appear on top of the bar
).encode(
    text='count:Q'
)

(bars + text).properties(height=900, title="Objects from Edinburgh from 1865 to 1880")