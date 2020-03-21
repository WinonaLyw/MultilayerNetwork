'''
retrieve point-of-interets
use parent category Food to retrieve all food locations
'''
# %% 
import pandas as pd

# %% 
df = pd.read_csv('data/dataset_TSMC2014_NYC.csv')

venueCategory = pd.read_csv('data/category.csv',index_col=0)
food = venueCategory[venueCategory['parentCategory']=='Food']

# %%
food_checkins = df[[(w in list(food['venueCategory'])) for w in df['venueCategory']]]

# %%
user_poi = food_checkins[['userId', 'venueId', 'venueCategory']].groupby(['userId', 'venueId'], as_index=False).count()
user_poi = user_poi.rename({'venueCategory':'weight'}, axis=1)

# %%
user_poi.to_csv('data/user_poi.csv')

# %%
food_locations = food_checkins.drop_duplicates(['venueId'])[['venueId','venueCategory','latitude','longitude']]

# %%
import smopy

M = smopy.Map((40.63080, -73.68390, 40.95840, -74.16000), z=13, margin=.5)
ax = M.show_mpl(figsize=(10, 12))
x, y = M.to_pixels(food_locations['latitude'], food_locations['longitude'])
ax.scatter(x, y, alpha=0.5)
plt.savefig('output/food_checkins.png')

# %%
food_locations.to_csv('data/poi.csv')

# %%
food2 = pd.merge(food_locations[['venueId','venueCategory']], food[['venueCategory','Food Type']], how='left', on='venueCategory')
food_type = list(set(food2['Food Type']))

cols = ['venueId1', 'venueId2', 'similarityDistance']
sim = []
for ftype in food_type:
    v_list = food2[food2['Food Type'] == ftype]

    ind_list = list(v_list.index)
    M = len(ind_list)
    for i1 in range(M-1):
        v1 = v_list.loc[ind_list[i1]]
        for i2 in range(i1+1,M):
            v2 = v_list.loc[ind_list[i2]]
            sim.append([v1['venueId'], v2['venueId'], 1 if v1['venueCategory'] == v2['venueCategory'] else 2])

sim_df = pd.DataFrame(sim, columns=cols)
# %%
sim_df.to_csv('data/poi_connection.csv')

# %%
