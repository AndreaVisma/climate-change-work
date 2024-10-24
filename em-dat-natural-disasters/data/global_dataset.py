"""
Script: global_dataset.py
Author: Andrea Vismara
Date: 23/10/2024
Description: creates a global dataset of natural disaster events
"""

#imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import os
import json
pio.renderers.default = 'browser'

dict_names = {}
with open('c:\\data\\general\\countries_dict.txt',
          encoding='utf-8') as f:
    data = f.read()
js = json.loads(data)
for k,v in js.items():
    for x in v:
        dict_names[x] = k

#read the EM-DAT data
emdat = pd.read_excel("c:\\data\\natural_disasters\\emdat_2024_07_all.xlsx")
emdat = emdat[(emdat["Start Year"] >= 2010) &
              (emdat["Disaster Group"] == "Natural")].copy()
emdat["Country"] = emdat["Country"].map(dict_names)

#create a dataset with dummy variables
emdat_tot = pd.pivot_table(data=emdat, columns =["Disaster Type"],
                               index=["Country", "Start Year"], values="Total Affected",
                           aggfunc="sum")
emdat_tot.fillna(0, inplace = True)
emdat_tot = emdat_tot.astype(int)
emdat_tot["total affected"] = emdat_tot.sum(axis=1)
emdat_tot.reset_index(inplace = True)
emdat_tot.to_excel("c:\\data\\natural_disasters\\emdat_country_type.xlsx", index = False)

def plot_disasters_year_country(country = 'Italy', disasters = ['total affected']):

    disasters.append("Start Year")
    df = emdat_tot[emdat_tot.Country == country][disasters].set_index("Start Year")

    fig, ax = plt.subplots(figsize = (8, 6))
    df.plot(kind = 'bar', ax = ax)
    plt.grid()
    plt.legend()
    plt.ylabel("Nr people affected")
    plt.title(f"Number of people affected from {'s, '.join(disasters[:-1])}, {country}")
    plt.show(block = True)

plot_disasters_year_country("Mexico", ["Earthquake", "Storm"])

emdat_tot.loc[emdat_tot["total affected"] > 0, "total affected"].map(np.log).hist(bins = 100)
plt.title("log distribution of total people affected by\nnatural disasters in country-years")
plt.show(block = True)