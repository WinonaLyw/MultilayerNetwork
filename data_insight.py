# %%
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# %%
df = pd.read_csv('data/dataset_TSMC2014_NYC.csv')

# %%
df.head()

# %%
df.columns.values

# %%
df1 = df.loc[(df['userId'] == 470) & (df['utcTimestamp'].str.contains('Sun'))]
df2 = df.loc[(df['userId'] == 470) & (df['utcTimestamp'].str.contains('Sat'))]

# %%
nyc = gpd.read_file('data/nycgiszoningfeatures_20/nyzd.shp')
nyc = nyc.to_crs(epsg=4326)
nyc.head()
# nyc.plot()

# %%
plt.figure(figsize=(10,10))
nyc.plot()
plt.scatter(df['longitude'],df['latitude'],c='y')

# %%
df3 = df[df['venueCategory'].str.contains('Restaurant')]


# %%
plt.scatter(df3['longitude'],df3['latitude'],c='y')


# %%
