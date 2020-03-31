import pandas as pd
import numpy as np

import geopy
from geopy.distance import VincentyDistance
import math


import visualisation as vs


class FoodRecommender:
    def __init__(self):
        self.users_n = pd.read_csv('data/user_connect.csv',index_col=0)
        self.poi = pd.read_csv('data/poi.csv', index_col=0)
        self.poi_connect_n = pd.read_csv('data/poi_connection.csv',index_col=0)
        self.user_poi_n = pd.read_csv('data/user_poi.csv',index_col=0)

    def recommend(self, userId, lat, lon):
        '''
        Parameter:
        userId: target user id
        lat, lon: loacation of the target user
        '''

        # get all food venue in the searching area
        lat1, lon1, lat2, lon2 = loc_window(lat, lon)
        f_all = self.get_all_Food(lat1, lon1, lat2, lon2)

        # get all similar users in the search area
        similar_users = self.get_similar_users(userId)

        # get all relevant users' food venue check-in activities in the searching area
        users_f_trget_link = self.get_target_similar_users_pois(f_all, similar_users)

        # get all food venues has all relevant users' check-in activities in the searching area
        f_target = self.get_Food_target(users_f_trget_link, f_all)

        # all target user food venues check-in history and all food venues involved
        user_f_link, f_user = self.get_user_Food(userId)

        f_target['is_target_user'] = 0
        f_user['is_target_user'] = 1
        users_f_trget_link['is_target_user'] = 0
        user_f_link['is_target_user'] = 1

        food_venues = f_target.append(f_user)
        # keep is_target_user = 1 if venue check-in by similar users and target user 
        food_venues = food_venues.loc[~food_venues.index.duplicated(keep='last')] 
        print ('food venues: total {0} records'.format(len(food_venues)))
        print (food_venues.head())

        users_food_link = users_f_trget_link.append(user_f_link)
        # keep is_target_user = 1 if venue check-in by similar users and target user 
        users_food_link = users_food_link.loc[~users_food_link.index.duplicated(keep='last')]
        print ('users and food venues link: total {0} records'.format(len(users_food_link)))
        print (users_food_link.head())

        self.visualiser = vs.NetworkVisualiser(similar_users, food_venues, users_food_link)

        users_food_link_user_based_rate = self.calculate_user_based_rate(userId, users_food_link, similar_users)
        print (users_food_link_user_based_rate.nlargest(10, 'user_based_rate'))

        print (user_f_link.head())
        users_food_link_item_based_rate = self.calculate_venue_based_rate(user_f_link, food_venues)
        print (users_food_link_item_based_rate.nlargest(10, 'item_based_rate'))

        users_food_link_rated = pd.merge(users_food_link_user_based_rate, users_food_link_item_based_rate, left_index=True, right_index=True,  how='outer')
        users_food_link_rated = users_food_link_rated.fillna(0)

        print (users_food_link_rated.head())

        users_food_link_rated['rate'] = users_food_link_rated.apply(lambda row: row['user_based_rate'] + row['item_based_rate'], axis = 1)
        
        return users_food_link_rated.nlargest(10, 'rate')
        

    def visualiseMultilayer(self, filename='multilayer_network'):
        self.visualiser.multilayer(filename)



    def get_all_Food(self, lat1, lon1, lat2, lon2):
        '''
        Parameter
        lat1, lon1, lat2, lon2: window boundary of search area
        Return
        all the food catefory check-ins in the search area
        '''
        poi_s1 = self.poi[[(w[1].latitude>min(lat1,lat2) and 
                w[1].latitude<max(lat1,lat2) and 
                    w[1].longitude>min(lon1,lon2) and 
                        w[1].longitude<max(lon1,lon2)) 
                            for w in self.poi.iterrows()]]
        print (poi_s1)
        return poi_s1


    def get_user_Food(self, userId) :
        '''
        Return 
        food category chick-ins of the target user
        '''
        # user_poi of the target user
        user_poi_s2 = pd.merge(self.user_poi_n[self.user_poi_n['userId'] == userId], self.poi, how='left', on='venueId')
        poi_s2 = user_poi_s2[['venueId','venueCategory','latitude','longitude']]
        print (poi_s2)
        return user_poi_s2, poi_s2

    def get_similar_users(self, userId) :
        # select similar user of the interested user
        users_s1 = self.users_n[self.users_n.userId1 == userId]

        return users_s1

    def get_target_similar_users_pois(self, pois, similar_users):
        '''
        Parameter
        pois:   food catgeory check-in venues in the seacrh area
        similar_users: target user and similar users with similarity
        Return 
        dataframe of target user and similar users in the search area, 
        together with the locations they have checked-in in the search 
        area
        '''

        # inner join user_poi table and selected pois
        # to select from the table only the ones related to selected poi
        user_poi_s1 = pd.merge(self.user_poi_n,pois,how='right', on='venueId')

        # all user involved, target user and similar users
        userIds_s = list(set(similar_users['userId1']).union(set(similar_users['userId2'])))

        # all connection of the relavant users and location in the selected area
        user_poi_s1 = user_poi_s1[[w[1]['userId'] in userIds_s for w in user_poi_s1.iterrows()]]

        return user_poi_s1
    
    def get_Food_target(self, users_pois, pois):
        '''
        Parameter
        user_pois:  dataframe of target user and similar users in the search area, 
                    together with the locations they have checked-in in the search
                    area
        Return 
        target food category venues to reconmmend from 
        1. in the search area
        2. checked in by target user or similar users
        '''
        poi_s1 = pois[[w[1]['venueId'] in list(users_pois['venueId']) for w in pois.iterrows()]]

        print (poi_s1)
        return poi_s1

    def calculate_user_based_rate(self, userId, users_food_link, similar_users):
        user_poi = users_food_link[users_food_link['userId'] != userId]
        
        max_checkin_user = user_poi[['userId','weight']].groupby('userId').max()

        user_poi = pd.merge(user_poi, max_checkin_user, left_on='userId', right_index=True)

        s_users = similar_users[['userId2', 'similarity']].set_index('userId2')
        user_poi = pd.merge(user_poi, s_users, left_on='userId', right_index=True)
        user_poi = user_poi.rename(columns={'weight_y':'max_check-in','weight_x':'check-in'})

        user_poi['user_based_rate'] = user_poi.apply(lambda row: row['check-in'] / row['max_check-in'] * row['similarity'], axis =1)
        rec = user_poi[['venueId', 'venueCategory', 'latitude', 'longitude', 'user_based_rate']].groupby(['venueId', 'venueCategory', 'latitude', 'longitude']).sum()
        return rec


    def calculate_venue_based_rate(self, user_f_link, food_venues):
        food_sim = pd.DataFrame(self.food_similarity(food_venues), columns=['venueId1', 'venueId2', 'similarity'])
        food_sim = pd.merge(food_sim, user_f_link[['venueId', 'weight']].set_index('venueId'), left_on='venueId1', right_on='venueId')

        food_sim['item_based_rate'] = food_sim.apply(lambda row:row['similarity'] * row['weight'], axis=1)
        food_sim = food_sim.groupby('venueId2').sum()['item_based_rate']

        food_sim = pd.merge(food_venues[food_venues['is_target_user'] == 0], food_sim, left_on='venueId', right_index=True)

        max_sim = max(food_sim['item_based_rate'])
        food_sim['item_based_rate'] = food_sim.apply(lambda row: row['item_based_rate']/max_sim * 6,axis=1)

        return food_sim[['venueId', 'venueCategory', 'latitude', 'longitude', 'item_based_rate']].set_index(['venueId', 'venueCategory', 'latitude', 'longitude'])


    def food_similarity(self, food_venues):
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


def loc_window(lat, lon):
    brng1 = 225 #Bearing is 315 degrees clockwise from north
    brng2 = 45 #Bearing is 135 degrees clockwise from north
    d = 5 #Distance in km

    lat1, lon1 = loc_from_distance(lat, lon, d, brng1)
    lat2, lon2 = loc_from_distance(lat, lon, d, brng2)
    return lat1, lon1, lat2, lon2

def loc_from_distance(lat, lon, d, brng):
    '''
    Parameters:
    lat, lon in degrees
    d in km
    brng in degrees

    Return: 
    lat, lon in degree
    '''
    origin = geopy.Point(lat, lon)
    destination = VincentyDistance(kilometers=d).destination(origin, brng)

    lat2, lon2 = destination.latitude, destination.longitude

    print(lat2,lon2)
    return lat2, lon2


def cal_distance(lat1, lon1, lat2, lon2):
    from math import sin, cos, sqrt, atan2

    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance