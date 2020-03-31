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
def cal_distance(lat1, lon1, lat2, lon2):
    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance

# %%
poi[['latitude','longitude']].describe()

'''
latitude	longitude
count	11489.000000	11489.000000
mean	40.748539	-73.975051
std	0.067544	0.084463
min	40.560883	-74.270118
25%	40.717264	-74.000441
50%	40.743934	-73.983023
75%	40.771831	-73.951187
max	40.988332	-73.683975
'''
# lat1=40.780368902469434
# lat2=40.71669373711954
# lon1=-74.01693433928067
# lon2=-73.93320759226746
# cal_distance(lat1, lon1, lat2, lon2)





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


available_poi = len(poi_s1)                            
# poi_s = poi.sample(100)

# inner join user_poi table and selected poi
# to select from the table only the ones related to selected poi
user_poi_s1 = pd.merge(user_poi_n,poi_s1,how='right', on='venueId')

# user_poi of the target user
user_poi_s2 = pd.merge(user_poi_n[user_poi_n['userId'] == userId], poi, how='left', on='venueId')
poi_s2 = user_poi_s2[['venueId','venueCategory','latitude','longitude']]

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
# %% construct graph nodes
# PoI layer
# poi connect of the sample pois
venueCategory = pd.read_csv('data/category.csv',index_col=0)
food = venueCategory[venueCategory['parentCategory']=='Food']

poi_s = poi_s1.append(poi_s2)
poi_s = poi_s.loc[~poi_s.index.duplicated(keep='last')] #'first'

number_of_poi_for_prediction = len(poi_s)

poi_nodes = poi_s
poi_edges = []

less_edge = True
if not less_edge:
    #  version 1
    poi_nodes = pd.merge(poi_s, food[['venueCategory','Food Type']], how='left', on='venueCategory')

    poi_nodes = poi_nodes.reset_index(drop=True)

    food_type = list(set(poi_nodes['Food Type']))

    for ftype in food_type:
        v_list = poi_nodes[poi_nodes['Food Type'] == ftype]

        ind_list = list(v_list.index)
        M = len(ind_list)
        for i1 in range(M-1):
            v1 = v_list.loc[ind_list[i1]]
            for i2 in range(i1+1,M):
                v2 = v_list.loc[ind_list[i2]]
                poi_edges.append([ind_list[i1], ind_list[i2], 1 if v1['venueCategory'] == v2['venueCategory'] else 2])
else:
# version 2
    poi_nodes = poi_nodes.reset_index(drop=True)
    food_type = list(set(poi_nodes['venueCategory']))
    for ftype in food_type:
        v_list = poi_nodes[poi_nodes['venueCategory'] == ftype]

        ind_list = list(v_list.index)
        M = len(ind_list)
        for i1 in range(M-1):
            v1 = v_list.loc[ind_list[i1]]
            for i2 in range(i1+1,M):
                v2 = v_list.loc[ind_list[i2]]
                poi_edges.append([ind_list[i1], ind_list[i2], 1])

## User layer
# user_nodes = pd.Series(userIds_s, index=range(len(poi_nodes), len(poi_nodes) + len(userIds_s)))
df = pd.read_csv('data/dataset_TSMC2014_NYC.csv')
user_nodes = df[[w in userIds_s for w in df['userId']]].groupby('userId', as_index=False).mean()[['userId','latitude','longitude']]
user_nodes = user_nodes.set_index(pd.Index(range(len(poi_nodes), len(poi_nodes) + len(user_nodes))))
user_edges = []
for row in users_s1.iterrows():
    ind1 = user_nodes[user_nodes['userId'] == row[1]['userId1']].index[0]
    ind2 = user_nodes[user_nodes['userId'] == row[1]['userId2']].index[0]
    user_edges.append((ind1, ind2, row[1]['similarity']))

# %% Define the type of interconnection between the layers
N = len(poi_nodes)+len(user_nodes)
N1 = len(poi_nodes)
adj_block = mx.lil_matrix(np.zeros((N,N)))

user_poi_s = user_poi_s1.append(user_poi_s2)
user_poi_s = user_poi_s.loc[~user_poi_s.index.duplicated(keep='last')]

for row in user_poi_s.iterrows():
    user_ind = user_nodes[user_nodes['userId'] == row[1]['userId']].index[0]
    pos_ind = poi_nodes[poi_nodes['venueId'] == row[1]['venueId']].index[0]

    adj_block[pos_ind, user_ind] = row[1]['weight'] 

adj_block += adj_block.T

# %% multilayer network
poi_layer = nx.Graph(layer='POI')
poi_layer.add_nodes_from(poi_nodes.index.values)
poi_layer.add_weighted_edges_from(poi_edges)

user_layer = nx.DiGraph(layer='User')
user_layer.add_nodes_from(user_nodes.index.values)
user_layer.add_weighted_edges_from(user_edges)

mg = mx.MultilayerGraph(list_of_layers=[poi_layer,user_layer], inter_adjacency_matrix=adj_block)

m = Basemap(
        projection='merc',
        llcrnrlon=lon1,
        llcrnrlat=lat1,
        urcrnrlon=lon2,
        urcrnrlat=lat2,
        lat_ts=0,
        resolution='i',
        suppress_ticks=True)

# position in decimal lat/lon
lats=list(poi_nodes['latitude'])
lons=list(poi_nodes['longitude'])
# convert lat and lon to map projection
x,y=m(lons,lats)

ppos = {}
n=0
for v in poi_nodes.index:
    ppos[v]=np.asarray([x[n],y[n]])
    n+=1

# position in decimal lat/lon
lats=list(user_nodes['latitude'])
lons=list(user_nodes['longitude'])
# convert lat and lon to map projection
x,y=m(lons,lats)
n=0
for v in user_nodes.index:
    ppos[v]=np.asarray([x[n],y[n]])
    n+=1

node_of_target_user = user_nodes[user_nodes['userId'] == userId].index[0]
    
# upos = mx.kamada_kawai_layout(user_layer)
# ppos.update(upos)
# %%
pos = mx.get_position(
                mg,
                ppos,
                layer_vertical_shift=1000.0,
                layer_horizontal_shift=400.0,
                proj_angle=0.2)


fig, ax2 = plt.subplots(figsize=(10,5))
# ax2.axis('off')
ax2.set_title('Multilayer Network of User and PoI')

mg.set_edges_weights(inter_layer_edges_weight=3)
mg.set_intra_edges_weights(layer=0,weight=5)
# mg.set_intra_edges_weights(layer=1,weight=2)

mx.draw_networkx(mg,pos=pos,ax=ax2,node_size=50,with_labels=False,
                node_color=['y' if a < N1 else ('brown' if a == node_of_target_user else 'g') for a in mg.nodes()],
                edge_color=[mg[a][b]['weight'] for a,b in mg.edges()], edge_cmap=plt.cm.Blues)
   
# plt.show()
plt.savefig('output/multilayer_network_2.png')

