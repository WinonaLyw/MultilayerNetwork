'''
create multi-index column for user location dataframe
level 0: parent category ['Shop & Services', 'Food'...]
level 1: venueCategory
'''
# %%
import pandas as pd

# %%
venueCategory = pd.read_csv('data/category.csv',index_col=0)
user_loc = pd.read_csv('data/user_loc_count.csv',index_col=0)

# %%
multi_ind_cols = venueCategory[['parentCategory','venueCategory']].values.T

user_loc.columns = pd.MultiIndex.from_arrays(multi_ind_cols)

# %%
parentCategory = list(set(venueCategory.parentCategory))

user_loc.reindex(parentCategory, axis=1, level=0)

# %%
user_loc.to_csv('data/user_loc_count.parentCategory.csv')

# %%
