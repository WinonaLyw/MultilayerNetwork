class NetworkVisualiser:
    # %%

    def __init__(self, similar_users, poi, user_poi):
        '''
        Parameters
        poi_s1: venues to recommend
        poi_s2: venues checked in by target users
        user_poi_s1: linkage of venues to recommend and similar users  
        user_poi_s2: linkage of tagert user and checked-in venues  
        '''
        self.similar_users = similar_users
        self.poi_s = poi
        self.user_poi_s = user_poi

        self.userIds_s = userIds_s = list(set(similar_users['userId1']).union(set(similar_users['userId2'])))
        self.prepare_nodes_and_edges()

        
    def prepare_nodes_and_edges(self):
        import pandas as pd

        # PoI layer
        # poi connect of the sample pois
        self.poi_edges = []

        self.poi_nodes = self.poi_s.reset_index(drop=True)
        food_type = list(set(self.poi_nodes['venueCategory']))
        for ftype in food_type:
            v_list = self.poi_nodes[self.poi_nodes['venueCategory'] == ftype]

        print (self.poi_nodes)

        ind_list = list(v_list.index)
        M = len(ind_list)
        for i1 in range(M-1):
            v1 = v_list.loc[ind_list[i1]]
            for i2 in range(i1+1,M):
                v2 = v_list.loc[ind_list[i2]]
                self.poi_edges.append([ind_list[i1], ind_list[i2], 1])

        print (self.poi_edges)

        ## User layer
        df = pd.read_csv('data/dataset_TSMC2014_NYC.csv')
        self.user_nodes = df[[w in self.userIds_s for w in df['userId']]].groupby('userId', as_index=False).mean()[['userId','latitude','longitude']]
        self.user_nodes = self.user_nodes.set_index(pd.Index(range(len(self.poi_nodes), len(self.poi_nodes) + len(self.user_nodes))))
        self.user_edges = []
        for row in self.similar_users.iterrows():
            ind1 = self.user_nodes[self.user_nodes['userId'] == row[1]['userId1']].index[0]
            ind2 = self.user_nodes[self.user_nodes['userId'] == row[1]['userId2']].index[0]
            self.user_edges.append((ind1, ind2, row[1]['similarity']))

        ## 
        # # PoI single layer

        # venueCategory = pd.read_csv('data/category.csv',index_col=0)
        # food = venueCategory[venueCategory['parentCategory']=='Food']

        # poi_edges_complex = []
        # poi_nodes_complex = pd.merge(poi_s, food[['venueCategory','Food Type']], how='left', on='venueCategory')

        # poi_nodes_complex = poi_nodes_complex.reset_index(drop=True)

        # food_type = list(set(poi_nodes_complex['Food Type']))

        # for ftype in food_type:
        #     v_list = poi_nodes_complex[poi_nodes_complex['Food Type'] == ftype]

        #     ind_list = list(v_list.index)
        #     M = len(ind_list)
        #     for i1 in range(M-1):
        #         v1 = v_list.loc[ind_list[i1]]
        #         for i2 in range(i1+1,M):
        #             v2 = v_list.loc[ind_list[i2]]
        #             poi_edges_complex.append([ind_list[i1], ind_list[i2], 1 if v1['venueCategory'] == v2['venueCategory'] else 2])



    def multilayer(self, filename='multilayer_network'):
        import numpy as np
        import matplotlib.pyplot as plt
        import multinetx as mx 
        import networkx as nx
        from mpl_toolkits.basemap import Basemap

        # %% Define the type of interconnection between the layers
        N = len(self.poi_nodes)+len(self.user_nodes)
        N1 = len(self.poi_nodes)
        adj_block = mx.lil_matrix(np.zeros((N,N)))

        for row in self.user_poi_s.iterrows():
            user_ind = self.user_nodes[self.user_nodes['userId'] == row[1]['userId']].index[0]
            pos_ind = self.poi_nodes[self.poi_nodes['venueId'] == row[1]['venueId']].index[0]

            adj_block[pos_ind, user_ind] = row[1]['weight'] 

        adj_block += adj_block.T


        # %% multilayer network
        poi_layer = nx.Graph(layer='POI')
        poi_layer.add_nodes_from(self.poi_nodes.index.values)
        poi_layer.add_weighted_edges_from(self.poi_edges)

        user_layer = nx.DiGraph(layer='User')
        user_layer.add_nodes_from(self.user_nodes.index.values)
        user_layer.add_weighted_edges_from(self.user_edges)

        mg = mx.MultilayerGraph(list_of_layers=[poi_layer,user_layer], inter_adjacency_matrix=adj_block)

        # venue position in decimal lat/lon
        lats_v=list(self.poi_nodes['latitude'])
        lons_v=list(self.poi_nodes['longitude'])
        
        min_lat = min(lats_v)
        max_lat = max(lats_v)
        min_lon = min(lons_v)
        max_lon = max(lons_v)

        # user position in decimal lat/lon
        lats_u=list(self.user_nodes['latitude'])
        lons_u=list(self.user_nodes['longitude'])

        min_lat = min(min_lat, min(lats_u))
        max_lat = max(max_lat, max(lats_u))
        min_lon = min(min_lon, min(lons_u))
        max_lon = max(max_lon, max(lons_u))

        m = Basemap(
                projection='merc',
                llcrnrlon=min_lon,
                llcrnrlat=min_lat,
                urcrnrlon=max_lon,
                urcrnrlat=max_lat,
                lat_ts=0,
                resolution='i',
                suppress_ticks=True)

        # convert lat and lon to map projection
        x,y=m(lons_v,lats_v)

        ppos = {}
        n=0
        for v in self.poi_nodes.index:
            ppos[v]=np.asarray([x[n],y[n]])
            n+=1

        # convert lat and lon to map projection
        x,y=m(lons_u,lats_u)
        n=0
        for v in self.user_nodes.index:
            ppos[v]=np.asarray([x[n],y[n]])
            n+=1

        target_userID = list(self.similar_users['userId1'])[0]
        node_of_target_user = self.user_nodes[self.user_nodes['userId'] == target_userID].index[0]
    
        for i in range(2):
            pos = mx.get_position(
                            mg,
                            ppos,
                            layer_vertical_shift=1000.0,
                            layer_horizontal_shift=400.0,
                            proj_angle=0.2)


            fig, ax2 = plt.subplots(figsize=(10,5))
            # ax2.axis('off')
            ax2.set_title('Multilayer Network of User and PoI (Target User ID: {0})'.format(target_userID))

            mg.set_edges_weights(inter_layer_edges_weight=3)
            mg.set_intra_edges_weights(layer=0,weight=5)
            # mg.set_intra_edges_weights(layer=1,weight=2)

            mx.draw_networkx(mg,pos=pos,ax=ax2,node_size=50,with_labels=False,
                            node_color=['y' if a < N1 else ('brown' if a == node_of_target_user else 'g') for a in mg.nodes()],
                            edge_color=[mg[a][b]['weight'] for a,b in mg.edges()], edge_cmap=plt.cm.Blues)
        
        # plt.show()
        plt.savefig('output/{0}.png'.format(filename), dpi=500, bbox_inches='tight')


def locations_on_map(df, lat, lon, min_lat, min_lon, max_lat, max_lon, filename='recommend') :
    import smopy
    import matplotlib.pyplot as plt

    M = smopy.Map((min_lat, min_lon-0.05, max_lat, max_lon+0.05), z=13, margin=0.005)

    x, y = M.to_pixels(df['latitude'], df['longitude'])

    x1, y1 = M.to_pixels(lat, lon)

    ax = M.show_mpl(figsize=(10, 6))

    # ax.scatter(x, y, c='y', label='Recommended Food Venues')

    cate = list(df['venueCategory'])
    for i, txt in enumerate(cate):
        # ax.annotate(txt, (x[i], y[i]))
        ax.scatter(x[i], y[i], marker='x', color='c', label='Recommended Food Venues')
        ax.text(x[i]+0.3, y[i], txt, fontsize=9)

    ax.scatter(x1, y1, c='r', label='User Location')
    plt.savefig('output/{0}.png'.format(filename), dpi=500, bbox_inches='tight')
    plt.close()
