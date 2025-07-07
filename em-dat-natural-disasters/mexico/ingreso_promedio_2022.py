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
emdat = pd.read_excel("C:\\git-projects\\climate-change-work\\mexico_updated.xlsx")
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

####
##data remittances
file =  'remittances_state_municipio'
df = pd.read_excel(f"c:\\data\\remittances\\mexico\\{file}.xlsx",
                   skiprows=9)
df = df.iloc[8:,:]

df = pd.melt(df, id_vars="Título", value_vars=df.columns.tolist()[1:], value_name="mln_USD_remesas")
df.rename(columns = {"Título": "Three months period starting"}, inplace = True)
df['entity_type'] = 'state'
df.loc[df.variable.str.contains('Municipio'), "entity_type"] = 'municipio'
df['state'] = None
df.loc[df.entity_type == 'state', "state"] = df.loc[df.entity_type == 'state'].variable.apply(lambda x: x.split(', ')[1])
df['state'].ffill(inplace=True)
df['municipio'] = None
df.loc[df.entity_type == 'municipio', "municipio"] = df.loc[df.entity_type == 'municipio'].variable.apply(lambda x: x.split(', ')[3])

df.drop(columns = 'variable', inplace = True)

##plot remittances received by state
gdf = gpd.read_file("c:\\data\\geo\\world_admin2\\World_Administrative_Divisions.shp")
gdf = gdf[(gdf.COUNTRY == "Mexico") & (gdf.LAND_RANK == 5)][['NAME', 'geometry']]
gdf.sort_values('NAME', inplace = True)
gdf.rename(columns = {'NAME' : 'state'}, inplace = True)

miss = ['Coahuila de Zaragoza','Veracruz de Ignacio de la Llave', 'Michoacán de Ocampo','México']
fix = ['Coahuila', 'Veracruz', 'Michoacán', 'Estado de México']
dict_names = dict(zip(miss, fix))
gdf.loc[gdf.state.isin(miss), 'state'] = (
    gdf.loc[gdf.state.isin(miss), 'state'].map(dict_names))

df_state = df[df.entity_type == 'state'].merge(gdf, on='state')
df_state = gpd.GeoDataFrame(df_state, geometry = 'geometry')
df_state = df_state[df_state['Three months period starting'].dt.year > 2023]

emdat = pd.read_excel("C:\\git-projects\\climate-change-work\\mexico_updated.xlsx")
emdat = emdat[~emdat.Latitude.isna()]
emdat.sort_values('date_start', ascending = False, inplace = True)
colors = ['blue', 'red', 'lightblue', 'orange', 'gold','pink', 'brown']
colors = dict(zip(emdat["Disaster Type"].unique(), colors))

### only remittances
fig = go.Figure()
fig = fig.add_trace(go.Choroplethmapbox(geojson=json.loads(df_state['geometry'].to_json()),
                                        locations=df_state.index,
                                        z=df_state["mln_USD_remesas"],
                                        text=df_state['state'],
                                        hovertemplate=
                                        '<br>State: %{text}' +
                                        '<br>Remittances per state<br> (2024, Q1): %{z:,.0f} mln USD',
                                        colorscale="speed_r", marker_opacity=0.7, colorbar_title="Remittances per state<br>(2024Q1, mln USD)",
                                        reversescale=True))
fig.update_layout(
    hovermode='closest',mapbox=dict(accesstoken=mapbox_access_token,bearing=0,center=go.layout.mapbox.Center(lat=23,lon=-99),
    pitch=0,zoom=4))
fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
fig.update_layout(title = 'Remittances per state, 2024Q1')
fig.update_geos(fitbounds="locations", lataxis_showgrid=True, lonaxis_showgrid=True, showcountries=True)
fig.write_html(os.getcwd() + "\\em-dat-natural-disasters\\mexico\\plots\\remittances_geo_2024q1.html")
fig.show()

##### with remittances

fig = go.Figure()
fig = fig.add_trace(go.Choroplethmapbox(geojson=json.loads(df_state['geometry'].to_json()),
                                        locations=df_state.index,
                                        z=df_state["mln_USD_remesas"],
                                        text=df_state['state'],
                                        hovertemplate=
                                        '<br>State: %{text}' +
                                        '<br>Remittances per state<br> (2024, Q1): %{z:,.0f} mln USD',
                                        colorscale="speed_r", marker_opacity=0.7, colorbar_title="Remittances per state<br>(2024Q1, mln USD)",
                                        reversescale=True))
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
    hovermode='closest',mapbox=dict(accesstoken=mapbox_access_token,bearing=0,center=go.layout.mapbox.Center(lat=23,lon=-99),
    pitch=0,zoom=4))
fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
fig.update_layout(title = 'Remittances per state, 2024Q1')
fig.update_geos(fitbounds="locations", lataxis_showgrid=True, lonaxis_showgrid=True, showcountries=True)
fig.write_html(os.getcwd() + "\\em-dat-natural-disasters\\mexico\\plots\\remittances and natural disasters.html")
fig.show()
