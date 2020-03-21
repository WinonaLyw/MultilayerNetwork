# %%
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import math


# %%
user_loc1 = pd.read_csv('data/grouped_user_loc_count.parentCategory.csv', index_col=0)

print (user_loc1.columns)

M = len(user_loc1)

'''
set similarity level
6 levels 
very 5 nearest neibghours in each level
'''
N = 6
K = 5
# %%
nn = NearestNeighbors(n_neighbors=N*K+1, metric='euclidean')
nn.fit(user_loc1)
dist, ind = nn.kneighbors(user_loc1, return_distance=True)

# %%
cols = ['userId1', 'userId2', 'similarityDistance']
sim = []

for i in range(len(ind)):
    for n in range(N):
        for j in range(n*K+1, (n+1)*K+1):
            sim.append([user_loc1.index[i], user_loc1.index[ind[i][j]], n+1])
# %%
sim_df = pd.DataFrame(sim, columns=cols)
sim_df.to_csv('data/user_connect.csv')

# %%
