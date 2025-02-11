import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')

df_nat = pd.read_csv("C:\\Data\\my_datasets\\weekly_remittances\\weekly_disasters.csv")
df_nat["week_start"] = pd.to_datetime(df_nat["week_start"])
df_nat["year"] = df_nat.week_start.dt.year

df_group = df_nat[['year', 'total_affected', 'type']].groupby(['year', 'type']).sum().reset_index()
df_group = df_group[df_group.year > 2010]
df_group = df_group[df_group.type.isin(['Drought', 'Flood', 'Earthquake'])]

df_pivot = pd.pivot(df_group, index='year', columns='type', values='total_affected')
df_pivot.sort_index(ascending=False, inplace = True)
fig,ax = plt.subplots(figsize = (6,6))
df_pivot.plot(kind='barh', stacked=True, ax = ax)
fig.savefig("C:\\git-projects\\climate-change-work\\plots\\trend_2010-2024.svg", bbox_inches = 'tight')
plt.show(block = True)