# %%
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import math

# %%
user_loc1 = pd.read_csv('data/grouped_user_loc_count.parentCategory.csv', index_col=0)
user_loc2 = pd.read_csv('data/user_loc_count.parentCategory.csv', index_col=0, header=[0,1])

print (user_loc1.columns)

M = len(user_loc1)
K = int(math.sqrt(M))

# %%
sample = user_loc1.sample(200)

# %% Distance Matrix
def dist_matrix(df):
    nn = NearestNeighbors(n_neighbors=len(df), metric='euclidean')
    nn.fit(df)
    dist, ind = nn.kneighbors(df, return_distance=True)

    print ('Euclidean: mean distance: %.1f, minimum distance: %.1f, maximum distance: %.1f'%(np.mean(dist), np.min(dist), np.max(dist)))
    nn_e = []
    for i in range(len(dist)):
        d = [dist[i,list(ind[i]).index(w)] for w in range(len(dist))]
        nn_e.append(d)
    return nn_e

class similarity_calculator:
    def __init__(self, data):
        self.data = data
        self.boxplot_values(np.asarray([item for sublist in data for item in sublist]))

    def boxplot_values(self, data):
        self.median = np.median(data)
        self.upper_quartile = np.percentile(data, 75)
        self.lower_quartile = np.percentile(data, 25)

        iqr = self.upper_quartile - self.lower_quartile
        self.upper_whisker = data[data<=self.upper_quartile+1.5*iqr].max()
        self.lower_whisker = data[data>=self.lower_quartile-1.5*iqr].min()

    def calculate_similarity_distance(self, v):
        '''
        similarity define:
        6 - least similar, v > upper_whisker
        5 - less similar, upper_quartile < v <= upper_whisker
        4 - average lower, median < v <= upper_whisker
        3 - average higher, lower_quartile < v <= median
        2 - more similar, lower_whisker < v <= lower_quartile
        1 - most similar, v <= lower_whisker
        '''
        if v > self.upper_whisker:
            return 6
        elif v > self.upper_quartile:
            return 5
        elif v > self.median:
            return 4
        elif v > self.lower_quartile:
            return 3
        elif v > self.lower_whisker:
            return 2
        else :
            return 1

# %%
dm = dist_matrix(user_loc1)

# %%
ax = sns.heatmap(dm, cmap = "BuGn_r")
ax.invert_yaxis()
plt.show()

# %%
sc = similarity_calculator(dm)
cols = ['userId1', 'userId2', 'similarityDistance']
sim = []
for i in range(len(dm)):
    for j in range(i+1, len(dm[i])):
        sim.append([user_loc1.index[i], user_loc1.index[j], sc.calculate_similarity_distance(dm[i][j])])
# %%
sim_df = pd.DataFrame(sim, columns=cols)

# %%
sim_df.to_csv('data/user_similarity_dist.csv')

# %%
