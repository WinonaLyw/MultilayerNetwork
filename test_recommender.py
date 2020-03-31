# %%
import pandas as pd
import recommender as rcd
import visualisation

DEBUG = False
userId = 130

# %% get living-community
df = pd.read_csv('data/dataset_TSMC2014_NYC.csv')
target_df = df[df['userId'] == userId]

# %%
min_lat = df['latitude'].min()
max_lat = df['latitude'].max()
min_lon = df['longitude'].min()
max_lon = df['longitude'].max()

print (min_lon, min_lat, max_lon, max_lat)

target_min_lat = target_df['latitude'].min()
target_max_lat = target_df['latitude'].max()
target_min_lon = target_df['longitude'].min()
target_max_lon = target_df['longitude'].max()

print (target_min_lon, target_min_lat, target_max_lon, target_max_lat)

'''
-74.27476645 40.55085247 -73.6838252 40.98833172
-74.01881933 40.67383576 -73.96684885 40.79173407
'''

in_living = {'lon': -74.00000000, 'lat':40.74000000}
out_living = {'lon': -73.95000000, 'lat':40.81500000}

x_il, y_il, x_iu, y_iu = loc_window(in_living['lat'], in_living['lon'])
x_ol, y_ol, x_ou, y_ou = loc_window(out_living['lat'], out_living['lon'])

# %%
recommender = rcd.FoodRecommender()

# %% case 1, living-community recommendation
rec_i =recommender.recommend(userId, in_living['lat'], in_living['lon'])

# recommender.visualiseMultilayer('multilayer_network_inside_living_{0}'.format(userId))

print(rec_i)
rec_i = rec_i.reset_index()

visualisation.locations_on_map(rec_i, in_living['lat'], in_living['lon'], x_il, y_il, x_iu, y_iu, 'recommend_inside_{0}'.format(userId)) 

# %% case 2, out-of-living-community recommendation
rec_o = recommender.recommend(userId, out_living['lat'], out_living['lon'])

# recommender.visualiseMultilayer('multilayer_network_outside_living_{0}'.format(userId))

print(rec_o)
rec_o = rec_o.reset_index()

visualisation.locations_on_map(rec_o, out_living['lat'], out_living['lon'], x_ol, y_ol, x_ou, y_ou, 'recommend_outside_{0}'.format(userId)) 


# %%
user_checkin = pd.read_csv('data/user_loc_count.parentCategory.csv', index_col=0, header=[0,1])

user_food_pref = user_checkin.loc[userId]['Food']

user_food_pref.nlargest(10)


# %% visualise user living community and selected reference locations

if (DEBUG) :
    import smopy
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle as Rectangle

    M = smopy.Map((min_lat, min_lon-0.05, max_lat, max_lon+0.05), z=13, margin=0.005)

    x, y = M.to_pixels(target_df['latitude'], target_df['longitude'])


    # x2, y2 = M.to_pixels(df['latitude'], df['longitude'])
    x3, y3 = M.to_pixels(in_living['lat'], in_living['lon'])
    x4, y4 = M.to_pixels(out_living['lat'], out_living['lon'])

    x_il, y_il = M.to_pixels(x_il, y_il)
    x_iu, y_iu = M.to_pixels(x_iu, y_iu)
    l = abs(x_iu - x_il)

    x_ol, y_ol = M.to_pixels(x_ol, y_ol)
    x_ou, y_ou = M.to_pixels(x_ou, y_ou)


    x_c, y_c = M.to_pixels((max_lat + min_lat)/2, (max_lon + min_lon)/2)
    r = (M.to_pixels(min_lat, (max_lon + min_lon)/2)[1] - M.to_pixels(max_lat, (max_lon + min_lon)/2)[1])/2

    ax = M.show_mpl(figsize=(10, 6))

    circle = plt.Circle((x_c, y_c), r, color='lightgrey', alpha=0.6)
    ax.add_patch(circle)
    # ax.scatter(x2, y2, alpha=0.1, c='lightgrey', label='all check-ins')

    ax.scatter(x, y, c='y', label='living community')

    ax.scatter(x3, y3, c='r', label='inside living community')

    # ax.add_patch(plt.Rectangle((x_il, y_iu), l, l, alpha=0.3, color = 'r'))
    rectangleX = [x_iu, x_iu, x_il, x_il, x_iu]
    rectangleY = [y_iu, y_il, y_il, y_iu, y_iu]
    plt.plot(rectangleX, rectangleY, 'r--')
    # ax.scatter(x_iu, y_iu, c='r', alpha=0.4)

    rectangleX = [x_ou, x_ou, x_ol, x_ol, x_ou]
    rectangleY = [y_ou, y_ol, y_ol, y_ou, y_ou]
    plt.plot(rectangleX, rectangleY, 'g--')
    # ax.add_patch(Rectangle((x_ol, y_ou), l, l, alpha=0.3, color = 'g'))
    ax.scatter(x4, y4, c='g', label='outside living community')
    ax.legend()

    plt.savefig('output/living_community_{0}.png'.format(userId), dpi=500, bbox_inches='tight')
    plt.close()