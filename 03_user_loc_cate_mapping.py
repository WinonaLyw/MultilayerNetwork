'''
1. create multi-index column for user location dataframe
level 0: parent category ['Shop & Services', 'Food'...]
level 1: venueCategory

2. create grouped venueCategory
'''
# %%
import pandas as pd

# %%
venueCategory = pd.read_csv('data/category.csv',index_col=0)
user_loc = pd.read_csv('data/user_loc_count.csv',index_col=0)

# %%
interested_entertainment = venueCategory[['venueCategory','Entertainment Type']].dropna(axis=0)
entertainment_cols = [col for col in user_loc.columns.values if col in list(interested_entertainment.venueCategory)]

food_type = venueCategory[['venueCategory','Food Type']].dropna(axis=0)
food_cols = [col for col in user_loc.columns.values if col in list(food_type.venueCategory)]

# %% 
intersted_user_loc = user_loc[entertainment_cols + food_cols]

# %% retrieve map category and map to user_loc table
interested_venueCategory = venueCategory[[w in (entertainment_cols + food_cols) for w in venueCategory['venueCategory']]]
multi_ind_cols = interested_venueCategory[['parentCategory','venueCategory']].values.T

intersted_user_loc.columns = pd.MultiIndex.from_arrays(multi_ind_cols)

# %% sort columns on parent catefory
parentCategory = list(set(interested_venueCategory.parentCategory))

intersted_user_loc = intersted_user_loc.reindex(parentCategory, axis=1, level=0)

# # %% drop user with no interested location check-ins
# # Food visits
# food = intersted_user_loc['Food'].sum(axis=1)
# food.describe()
# no_food_ind = list(food[food==0].index)

# # Shop & Service, Arts & Entertainment, Outdoors & Recreation, Nightlife Spot
# leisure = intersted_user_loc[['Shop & Service', 'Arts & Entertainment', 'Outdoors & Recreation','Nightlife Spot']].sum(axis=1)
# leisure.describe()
# no_leisure_ind = list(leisure[leisure==0].index)

# intersted_user_loc = intersted_user_loc.drop(no_food_ind+no_leisure_ind,axis=0)

# %% save interested_user_loc
intersted_user_loc.to_csv('data/user_loc_count.parentCategory.csv')

# %% group locations
intersted_user_loc.columns = intersted_user_loc.columns.droplevel()
original_cols = intersted_user_loc.columns

for e in list(set(interested_entertainment['Entertainment Type'])):
    v_cate = list(interested_entertainment[interested_entertainment['Entertainment Type'] == e]['venueCategory'])
    intersted_user_loc[e] = [row[1].sum() for row in intersted_user_loc[v_cate].iterrows()]
    


for e in list(set(food_type['Food Type'])):
    v_cate = list(food_type[food_type['Food Type'] == e]['venueCategory'])
    intersted_user_loc[e] = [row[1].sum() for row in intersted_user_loc[v_cate].iterrows()]
    

intersted_user_loc = intersted_user_loc.drop(original_cols, axis=1)

# %%
intersted_user_loc.to_csv('data/grouped_user_loc_count.parentCategory.csv')

# %%
