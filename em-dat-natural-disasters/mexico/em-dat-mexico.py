"""
Script: em-dat-mexico.py
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
import plotly.express as px
import os
pio.renderers.default = 'browser'

mapbox_access_token = open("c:\\data\\geo\\mapbox_token.txt").read()

#read the EM-DAT data
emdat = pd.read_excel("c:\\data\\natural_disasters\\emdat_2024_07_all.xlsx")
emdat = emdat[(emdat.Country == "Mexico") &
              (~emdat["Total Affected"].isna()) &
              (emdat["Disaster Group"] == "Natural") &
              (emdat["Start Year"] >= 1995)].copy()
emdat.sort_values("Total Affected", ascending = False, inplace = True)

emdat.loc[~emdat["Admin Units"].isna(), "regions"] = (emdat.loc[~emdat["Admin Units"].isna(), "Admin Units"].
                                                          apply(lambda x: [i["adm1_name"] for i in ast.literal_eval(x) if "adm1_name" in i.keys()]))
emdat.loc[~emdat["Admin Units"].isna(), "admin2"] = (emdat.loc[~emdat["Admin Units"].isna(), "Admin Units"].
                                                          apply(lambda x: [i["adm2_name"] for i in ast.literal_eval(x) if "adm2_name" in i.keys()]))

emdat[['Start Year','Start Month', 'Start Day']] = (
    emdat[['Start Year','Start Month', 'Start Day']].fillna(1).astype(int))
emdat.rename(columns = dict(zip(['Start Year','Start Month', 'Start Day'],
                              ["year", "month", "day"])), inplace = True)
emdat["date_start"] = pd.to_datetime(emdat[["year", "month", "day"]])
emdat.drop(columns = ["year", "month", "day"], inplace = True)

emdat[['End Year','End Month', 'End Day']] = (
    emdat[['End Year','End Month', 'End Day']].fillna(12).astype(int))
emdat.rename(columns = dict(zip(['End Year','End Month', 'End Day'],
                              ["year", "month", "day"])), inplace = True)
emdat["date_end"] = pd.to_datetime(emdat[["year", "month", "day"]])
emdat.drop(columns = ["year", "month", "day"], inplace = True)

###keep only things for which we have coordinates
emdat = pd.read_excel("C:\\git-projects\\climate-change-work\\mexico_updated.xlsx")
emdat = emdat[~emdat.Latitude.isna()]
emdat.sort_values('date_start', ascending = False, inplace = True)

#plot all earthquakes
earth = emdat[emdat["Disaster Type"] == "Earthquake"].copy()
earth = earth[['Total Deaths', 'No. Injured', 'No. Affected', 'No. Homeless', "Total Damage ('000 US$)",
               'Total Affected', 'Latitude', 'Longitude', 'regions', 'admin2', 'date_start', 'date_end']]
earth.sort_values('date_start', ascending = False, inplace = True)

############
fig = go.Figure()
fig.add_trace(go.Scattermapbox(
    lon=earth['Longitude'],
    lat=earth['Latitude'],
    text=earth['date_start'].dt.strftime('%d-%m-%Y'),
    customdata=np.stack((earth['Total Affected'] / 1_000, earth['Total Deaths'], earth["Total Damage ('000 US$)"] / 1_000), axis = -1),
    hovertemplate=
    'Date: %{text}' +
    '<br>Total affected: %{customdata[0]:,.2f}k' +
    '<br>Total dead: %{customdata[1]:,.0f}'
    '<br>Total damages: %{customdata[2]:,.0f} mln US$',
    mode='markers',
    marker=go.scattermapbox.Marker(
        size = 4 * earth['Total Affected'].apply(lambda x: x**0.2),
        opacity=0.7,
        reversescale=True,
        autocolorscale=False,
        colorscale='Spectral',
        cmin=0,
        color=earth['Total Affected'],
        cmax=earth['Total Affected'].max(),
        colorbar_title="Number of people<br>affected by earthquake"
    )))
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

fig.update_layout(title = 'Earthquakes in Mexico, 1995-2024')
fig.update_geos(fitbounds="locations", lataxis_showgrid=True, lonaxis_showgrid=True, showcountries=True)
fig.write_html("C:\\git-projects\\climate-change-work\\em-dat-natural-disasters\\mexico\\plots\\earthquakes-1995-2024.html")
fig.show()

#### plot all disasters together
fig = go.Figure()

for disaster in emdat["Disaster Type"].unique():
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
            size = 4 * earth['Total Affected'].apply(lambda x: x**0.18),
            opacity=0.7,
            # reversescale=True,
            # autocolorscale=False,
            # colorscale='Spectral',
            # cmin=0,
            # color=earth['Total Affected'],
            # cmax=emdat['Total Affected'].max(),
            # colorbar_title="Number of people<br>affected by disaster"
        )))
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

fig.update_layout(title = 'All natural disasters in Mexico, 1995-2024')
fig.update_geos(fitbounds="locations", lataxis_showgrid=True, lonaxis_showgrid=True, showcountries=True)
fig.write_html(os.getcwd() + "\\em-dat-natural-disasters\\mexico\\plots\\all_natural_disasters-1995-2024.html")
fig.show()