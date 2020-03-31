# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import multinetx as mx 
import networkx as nx
from math import sin, cos, sqrt, atan2
from mpl_toolkits.basemap import Basemap


# %%
users_n = pd.read_csv('data/user_connect.csv',index_col=0)
poi = pd.read_csv('data/poi.csv', index_col=0)
poi_connect_n = pd.read_csv('data/poi_connection.csv',index_col=0)
user_poi_n = pd.read_csv('data/user_poi.csv',index_col=0)

# %%
in_living = {'lon': -74.00000000, 'lat':40.74000000}
out_living = {'lon': -73.95000000, 'lat':40.81500000}

lat1, lon1, lat2, lon2 = loc_window(in_living['lat'], in_living['lon'])
# lat1, lon1, lat2, lon2 = loc_window(out_living['lat'], out_living['lon'])

# %%
# import random
userId = 130#random.randint(1, 1083)

# %% sample poi in the target area
poi_s1 = poi[[(w[1].latitude>min(lat1,lat2) and 
                w[1].latitude<max(lat1,lat2) and 
                    w[1].longitude>min(lon1,lon2) and 
                        w[1].longitude<max(lon1,lon2)) 
                            for w in poi.iterrows()]]

poi_s1['is_target_user'] = 0
available_poi = len(poi_s1)                            
# poi_s = poi.sample(100)

# inner join user_poi table and selected poi
# to select from the table only the ones related to selected poi
user_poi_s1 = pd.merge(user_poi_n,poi_s1,how='right', on='venueId')

# user_poi of the target user
user_poi_s2 = pd.merge(user_poi_n[user_poi_n['userId'] == userId], poi, how='left', on='venueId')
poi_s2 = user_poi_s2[['venueId','venueCategory','latitude','longitude']]

poi_s2['is_target_user'] = 1
# %% select relevant users

# userIds_s = list(set(user_poi_s['userId']))
# users_s = users_n[[row[1]['userId2'] in userIds_s for row in users_n.iterrows()]]

# select similar user of the interested user
users_s1 = users_n[users_n.userId1 == userId]

# all user involved, target user and similar users
userIds_s = list(set(users_s1['userId1']).union(set(users_s1['userId2'])))

# all connection of the relavant users and location in the selected area
user_poi_s1 = user_poi_s1[[w[1]['userId'] in userIds_s for w in user_poi_s1.iterrows()]]

poi_s1 = poi_s1[[w[1]['venueId'] in list(user_poi_s1['venueId']) for w in poi_s1.iterrows()]]
# %% 
poi_s = poi_s1.append(poi_s2)
poi_s = poi_s.loc[~poi_s.index.duplicated(keep='last')] #'first'

number_of_poi_for_prediction = len(poi_s)


user_poi_s = user_poi_s1.append(user_poi_s2)
user_poi_s = user_poi_s.loc[~user_poi_s.index.duplicated(keep='last')]

# ==========recommend user_based============
# %% 
user_poi = user_poi_s[user_poi_s['userId'] != userId]

# %%
max_checkin_user = user_poi[['userId','weight']].groupby('userId').max()

user_poi = pd.merge(user_poi, max_checkin_user, left_on='userId', right_index=True)

# %%
s_users = users_s1[['userId2', 'similarity']].set_index('userId2')
user_poi = pd.merge(user_poi, s_users, left_on='userId', right_index=True)
user_poi = user_poi.rename(columns={'weight_y':'max_check-in','weight_x':'check-in'})

# %%
user_poi['user_based_rate'] = user_poi.apply(lambda row: row['check-in'] / row['max_check-in'] * row['similarity'], axis =1)

# %%
recommend = user_poi[['venueId', 'venueCategory', 'latitude', 'longitude', 'user_based_rate']].groupby(['venueId', 'venueCategory', 'latitude', 'longitude']).sum()

recommend.nlargest(10, 'user_based_rate')

# %%
coverage = number_of_poi_for_prediction / available_poi

# =====recommend item_based======
# %%
def food_similarity(food_venues):
    import pandas as pd

    venueCategory = pd.read_csv('data/category.csv',index_col=0)
    food = venueCategory[venueCategory['parentCategory']=='Food']

    food_sim = []
    food_v = pd.merge(food_venues, food[['venueCategory','Food Type']], how='left', on='venueCategory')

    food_type = list(set(food_v['Food Type']))

    for ftype in food_type:
        v_list = food_v[food_v['Food Type'] == ftype]

        v_list1 = v_list[v_list['is_target_user'] == 1]
        v_list2 = v_list[v_list['is_target_user'] == 0]
        
        for r1 in v_list1.iterrows():
            v1 = r1[1]
            for r2 in v_list2.iterrows():
                v2 = r2[1]
                food_sim.append([v1['venueId'], v2['venueId'], 2 if v1['venueCategory'] == v2['venueCategory'] else (1 if v1['Food Type'] == v2['Food Type'] else 0)])


    return food_sim
# %% 
food_sim = pd.DataFrame(food_similarity(poi_s), columns=['venueId1', 'venueId2', 'similarity'])
food_sim = pd.merge(food_sim, user_poi_s2[['venueId', 'weight']].set_index('venueId'), left_on='venueId1', right_on='venueId')

food_sim['item_based_rate'] = food_sim.apply(lambda row:row['similarity'] * row['weight'], axis=1)
food_sim = food_sim.groupby('venueId2').sum()['item_based_rate']

food_sim = pd.merge(poi_s[poi_s['is_target_user'] == 0], food_sim, left_on='venueId', right_index=True)

max_sim = max(food_sim['item_based_rate'])
food_sim['item_based_rate'] = food_sim.apply(lambda row: row['item_based_rate']/float(max_sim) * 6,axis=1)
food_sim.nlargest(10, 'item_based_rate')

# %%
users_food_link_rated = pd.merge(recommend, food_sim.set_index(['venueId', 'venueCategory', 'latitude', 'longitude']), left_index=True, right_index=True,  how='outer')
users_food_link_rated = users_food_link_rated.fillna(0)

users_food_link_rated['rate'] = users_food_link_rated.apply(lambda row: row['user_based_rate'] + row['item_based_rate'], axis = 1)
        
users_food_link_rated.nlargest(10, 'rate')

# %%