from sklearn.datasets import fetch_california_housing
import mglearn
import matplotlib.pyplot as plt
import numpy as np

boston = fetch_california_housing()
print("Data shape: {}".format(boston.data.shape))

X, y = mglearn.datasets.load_extended_boston()
print("X.shape: {}".format(X.shape))
mglearn.plots.plot_knn_classification(n_neighbors=3)
# plt.show()

X = np.array([[0, 1, 0, 1],
              [1, 0, 1, 1],
              [0, 0, 0, 1],
              [1, 0, 1, 0]])

y = np.array([0, 1, 0, 1])

counts = {}
for label in np.unique(y):
    # iterate over each class
    # count (sum) entries of 1 per feature
    print(label)
    print(X[y == label])
    counts[label] = X[y == label].sum(axis=0)

print("Feature counts:\n{}".format(counts))
# print(X[2])
