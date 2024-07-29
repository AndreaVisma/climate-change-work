"""
Script: em-ingreso_promedio_2022.py
Author: Andrea Vismara
Date: 23/07/2024
Description: Explores the data for natural disasters in mexico
"""
import numpy as np
#imports
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import numpy as np
import ast
import plotly.graph_objects as go
import plotly.io as pio
import json
import plotly.express as px
import os
from shapely import wkt

pio.renderers.default = 'browser'

mapbox_access_token = open("c:\\data\\geo\\mapbox_token.txt").read()

###geolocation data
mex_states = gpd.read_file("c:\\data\\geo\\world_admin2\\World_Administrative_Divisions.shp")
mex_states = mex_states[(mex_states.COUNTRY == "Mexico") & (mex_states.LAND_RANK == 5)]

##data ingreso promedio
df = pd.read_excel("c:\\data\\economic\\mexico\\ingreso_promedio_hogares_2022.xlsx",
                   skiprows = 4, nrows=33)
df.rename(columns={"Entidad federativa": "NAME"}, inplace = True)
df = df.merge(mex_states[["NAME", "geometry"]], on='NAME')
df = gpd.GeoDataFrame(df, geometry="geometry")

fig = go.Figure()
fig = fig.add_trace(go.Choroplethmapbox(geojson=json.loads(df['geometry'].to_json()),
                                        locations=df.index,
                                        z=df["Total"],
                                        text=df['NAME'],
                                        hovertemplate=
                                        '<br>State: %{text}' +
                                        '<br>Ingreso total promedio<br>por hogar (2022): %{z:,.0f} pesos',
                                        colorscale="speed", marker_opacity=0.7, colorbar_title="Ingreso del trabajo promedio<br>por hogar (2022, pesos)",
                                        reversescale=True))
fig.update_layout(
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=23,
            lon=-99
        ),
        pitch=0,
        zoom=4
    )
)
fig.update_layout(title = 'Ingreso medio total por hogar, Mexico, 2022')
fig.update_geos(fitbounds="locations", lataxis_showgrid=True, lonaxis_showgrid=True, showcountries=True)
fig.write_html(os.getcwd() + "\\em-dat-natural-disasters\\mexico\\plots\\total_ingreso_2022.html")
fig.show()

##emdat data
emdat = pd.read_excel(".\\mexico_updated.xlsx")
emdat = emdat[~emdat.Latitude.isna()]
emdat.sort_values('date_start', ascending = False, inplace = True)

#
colors = ['blue', 'red', 'lightblue', 'orange', 'gold','pink', 'brown']
colors = dict(zip(emdat["Disaster Type"].unique(), colors))
#
fig = go.Figure()
fig = fig.add_trace(go.Choroplethmapbox(geojson=json.loads(df['geometry'].to_json()),
                                        locations=df.index,
                                        z=df["Ingreso del trabajo"],
                                        text=df['NAME'],
                                        hovertemplate=
                                        '<br>State: %{text}' +
                                        '<br>Ingreso del trabajo promedio<br>por hogar (2022): %{z:,.0f} pesos',
                                        colorscale="speed", marker_opacity=0.7, colorbar_title="Ingreso del trabajo promedio<br>por hogar (2022, pesos)"))
for disaster in ['Storm', 'Earthquake', 'Flood', 'Drought', 'Extreme temperature']:
    earth = emdat[emdat["Disaster Type"] == disaster].copy()

    fig.add_trace(go.Scattermapbox(
        lon=earth['Longitude'],
        lat=earth['Latitude'],
        text=earth['date_start'].dt.strftime('%d-%m-%Y'),
        customdata=np.stack((earth['Total Affected'] / 1_000, earth['Total Deaths'], earth["Total Damage ('000 US$)"] / 1_000), axis = -1),
        hovertemplate=
        f'<b>{disaster}</b>' +
        '<br>Date: %{text}' +
        '<br>Total affected: %{customdata[0]:,.2f}k' +
        '<br>Total dead: %{customdata[1]:,.0f}'
        '<br>Total damages: %{customdata[2]:,.0f} mln US$',
        mode='markers',
        name = disaster,
        showlegend=True,
        marker=go.scattermapbox.Marker(
            size = earth['Total Affected'].apply(lambda x: x**0.26),
            opacity=0.8,
            color = colors[disaster]
        )))
fig.update_layout(
    hovermode='closest',
    mapbox=dict(
        style ="carto-positron",
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=23,
            lon=-99
        ),
        pitch=0,
        zoom=4),
    mapbox_layers = [{"visible" : False}]
    )

fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))
fig.update_layout(title = 'Ingreso medio del trabajo por hogar, Mexico, 2022 and natural disasters (1995-2024)')
fig.update_geos(fitbounds="locations", lataxis_showgrid=True, lonaxis_showgrid=True, showcountries=True)
fig.write_html(os.getcwd() + "\\em-dat-natural-disasters\\mexico\\plots\\ingreso_promedio_natural_disasters.html")
fig.show()
