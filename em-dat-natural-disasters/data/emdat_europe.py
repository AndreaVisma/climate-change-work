"""
Script: emdat_europe.py
Author: Andrea Vismara
Date: 23/10/2024
Description: have a look at the biggest natural disaster in Europe
"""

#imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import os
import ast
from utils import dict_names
pio.renderers.default = 'browser'


#read the EM-DAT data
emdat = pd.read_excel("c:\\data\\natural_disasters\\emdat_2024_07_all.xlsx")
df_eur = emdat[(emdat.Subregion == "Western Europe") &
              (~emdat["Total Affected"].isna()) &
              (emdat["Disaster Group"] == "Natural")].copy()
df_eur.sort_values("Total Affected", ascending = False, inplace = True)

df_eur.loc[~df_eur["Admin Units"].isna(), "regions"] = (df_eur.loc[~df_eur["Admin Units"].isna(), "Admin Units"].
                                                          apply(lambda x: [i["adm1_name"] for i in ast.literal_eval(x) if "adm1_name" in i.keys()]))
df_eur.loc[~df_eur["Admin Units"].isna(), "admin2"] = (df_eur.loc[~df_eur["Admin Units"].isna(), "Admin Units"].
                                                          apply(lambda x: [i["adm2_name"] for i in ast.literal_eval(x) if "adm2_name" in i.keys()]))