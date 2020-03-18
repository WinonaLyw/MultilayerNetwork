'''
load csv of download check-ins
groupby user and venueCategory
transform dataframe to user_id as index, venueCategory as columns
retrieve all venueCategory values and total visti count
'''

# %%
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# %%
df = pd.read_csv('data/dataset_TSMC2014_NYC.csv')

# %%
df.head()

print (df.columns.values)

# %% total check-ins per user
visit = df.groupby('userId').count()['venueCategory']

plt.subplot(121)
plt.boxplot(visit)
plt.subplot(122)
visit.hist()

visit.describe()

# %% save all categories to file
venueCategory = df[['userId', 'venueCategory']].groupby('venueCategory', as_index=False).count()
venueCategory = venueCategory.rename(columns={'userId':'count'})

venueCategory.to_csv('data/category.csv')

# %%
# user check-in category frequency
df3 = df[['userId', 'venueCategory']].groupby(['userId', 'venueCategory']).venueCategory.agg('count').to_frame('count')
df3 = df3.unstack().fillna(0)

df3.columns = df3.columns.droplevel()

df3.to_csv('data/user_loc_count.csv')

# %% Restaurant type locations
restaurant_keywords = ['Restaurant','Food','Joint','Deli','Diner',\
                    'Breakfast','Steakhouse','Pizza','Noodle',\
                    'Sandwich','Burrito','Fish & Chips','Salad',\
                    'Café','Coffee','Cupcake','Donut','Ice Cream',\
                    'Bagel','Taco','Snack','Candy','Brewery','Distillery',\
                    'Winery','Gastropub','Soup']

df4 = df[[any(s in cate for s in restaurant_keywords) for cate in df['venueCategory']]]


# %%
plt.scatter(df4['longitude'],df4['latitude'],c='y')

# %%
