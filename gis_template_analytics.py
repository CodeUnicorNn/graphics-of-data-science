import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster

# FIX: Loading the dataset directly via URL since gpd.datasets is deprecated
# This is the official 'naturalearth_lowres' dataset
url = "https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/world-countries.json"
world = gpd.read_file(url)

# Rename column to match ISO codes if necessary (depends on the source)
# For the URL above, the ID is already in the 'id' column
world = world.rename(columns={'id': 'iso_a3'})

# STEP 2: Prepare economic indicators (Same as before)
data = {
    'iso_a3': ['USA', 'CHN', 'IND', 'RUS', 'EGY', 'ETH', 'BRA', 'ZAF', 'SAU', 'ARE'],
    'investment_vol': [500, 450, 300, 200, 150, 120, 280, 180, 210, 195],
    'project_count': [50, 85, 40, 30, 25, 60, 35, 20, 15, 18]
}
df_finance = pd.DataFrame(data)

# STEP 3: Merge (Same as before)
world = world.merge(df_finance, how='left', left_on='iso_a3', right_on='iso_a3')
world['investment_vol'] = world['investment_vol'].fillna(0)

# STEP 4: Initialize interactive Folium map
# Centered on coordinates [20, 0] to show a global perspective
m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')

# STEP 5: Add Choropleth layer to visualize zones of influence
folium.Choropleth(
    geo_data=world,
    name='Global Financial Flows',
    data=world,
    columns=['iso_a3', 'investment_vol'],
    key_on='feature.properties.iso_a3',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Investment Volume (Relative Units)',
    highlight=True
).add_to(m)

# STEP 6: Add interactive Tooltips for data exploration
# This allows users to see specific metrics upon hovering
style_function = lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.1, 'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}

NIL = folium.features.GeoJson(
    world,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name', 'investment_vol', 'project_count'],
        aliases=['Country: ', 'Volume: ', 'Projects: '],
        style=("background-color: white; color: #333333; font-family: sans-serif; font-size: 12px; padding: 10px;")
    )
)
m.add_child(NIL)
m.keep_in_front(NIL)

# STEP 7: Export results
m.save('geospatial_economic_analysis.html')
print("Interactive map has been generated: geospatial_economic_analysis.html")