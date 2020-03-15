# %%
from sklearn.neighbors import NearestNeighbors

# %% KDTree

nn = neighbors.NearestNeighbors(n_neighbors=2, metric='euclidean')
nn.fit(x)
dist, ind = nn.kneighbors(x, n_neighbors=2)


plt.plot(dist)


# %% Ball Tree
