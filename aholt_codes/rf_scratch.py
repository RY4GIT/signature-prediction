# https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance_multicollinear.html

import pandas
from sklearn.inspection import permutation_importance
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, KFold

# Author: Anne Holt (@annieholt)
# Date: 2024


# rf_data = pandas.read_csv("E:/SDSU_GEOG/Thesis/Data/RandomForest/BFI_attributes_test_data.csv", header=0, index_col=0)
# rf_data = pandas.read_csv("E:/SDSU_GEOG/Thesis/Data/RandomForest/sigs_attributes_master.csv")
rf_data = pandas.read_csv("E:/SDSU_GEOG/Thesis/Data/RandomForest/sigs_attributes_caravan_master.csv")

# for camels data
# removing categorical data and dropping NAs, for now
# and just keeping BFI for now
# rf_data_2 = rf_data.drop(['gauge_id', 'low_prec_timing', 'high_prec_timing', 'geol_1st_class',
#                           'glim_1st_class_frac', 'dom_land_cover', 'dom_land_cover_frac',
#                           'non_giw_frac', 'geol_major_age_ma', 'TotalRR', 'RR_Seasonality', 'EventRR',
#                           'Recession_a_Seasonality', 'AverageStorage',
#                           'RecessionParameters_a', 'RecessionParameters_b', 'RecessionParameters_c',
#                           'MRC_num_segments', 'First_Recession_Slope', 'Mid_Recession_Slope', 'Spearmans_rho',
#                           'EventRR_TotalRR_ratio', 'VariabilityIndex', 'BaseflowRecessionK'], axis=1)


# for caravan data
# removing categorical data and dropping NAs, for now
# and just keeping BFI for now
rf_data_2 = rf_data.drop(['gauge_id', 'geol_major_age_ma', 'non_giw_frac',
                          'EventRR', 'TotalRR', 'RR_Seasonality',
                          'Recession_a_Seasonality', 'AverageStorage',
                          'RecessionParameters_a', 'RecessionParameters_c',
                          'MRC_num_segments', 'First_Recession_Slope', 'Mid_Recession_Slope', 'Spearmans_rho',
                          'EventRR_TotalRR_ratio', 'VariabilityIndex', 'BaseflowRecessionK', 'BFI'], axis=1)


rf_data_3 = rf_data_2.dropna()
# print(rf_data_3)

X = rf_data_3.drop('RecessionParameters_b', axis=1)
y = rf_data_3['RecessionParameters_b']
# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2)



clf = RandomForestRegressor(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
print(f"R-squared on test data: {clf.score(X_test, y_test):.2f}")

# Perform 10-fold cross-validation
cv_scores = cross_val_score(clf, X, y, cv=KFold(n_splits=10, shuffle=True, random_state=42))

# Print cross-validation scores
print(f"Cross-validation R-squared scores: {cv_scores}")
print(f"Mean R-squared from cross-validation: {cv_scores.mean():.2f}")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_permutation_importance(clf, X, y, ax):
    result = permutation_importance(clf, X, y, n_repeats=10, random_state=42, n_jobs=2)
    perm_sorted_idx = result.importances_mean.argsort()

    ax.boxplot(
        result.importances[perm_sorted_idx].T,
        vert=False,
        labels=X.columns[perm_sorted_idx],
    )
    ax.axvline(x=0, color="k", linestyle="--")
    return ax

mdi_importances = pd.Series(clf.feature_importances_, index=X_train.columns)
tree_importance_sorted_idx = np.argsort(clf.feature_importances_)
tree_indices = np.arange(0, len(clf.feature_importances_)) + 0.5

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
mdi_importances.sort_values().plot.barh(ax=ax1)
ax1.set_xlabel("Gini importance")
plot_permutation_importance(clf, X_train, y_train, ax2)
ax2.set_xlabel("Decrease in accuracy score")
fig.suptitle(
    "Impurity-based vs. permutation importances on multicollinear features (train set)"
)
_ = fig.tight_layout()


from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
from scipy.stats import spearmanr

import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
from scipy.stats import spearmanr

# Assuming X is your feature matrix
corr = spearmanr(X).correlation

# Ensure the correlation matrix is symmetric
corr = (corr + corr.T) / 2
np.fill_diagonal(corr, 1)

# Create a distance matrix
distance_matrix = 1 - np.abs(corr)

# Perform hierarchical clustering using Ward's linkage
dist_linkage = hierarchy.ward(squareform(distance_matrix))

# Create a dendrogram
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
dendro = hierarchy.dendrogram(dist_linkage, labels=X.columns.to_list(), ax=ax1, leaf_rotation=90)
dendro_idx = np.arange(0, len(dendro["ivl"]))

# Create a heatmap with correlation values
heatmap = ax2.imshow(corr[dendro["leaves"], :][:, dendro["leaves"]], cmap='coolwarm')

# Add colorbar
cbar = fig.colorbar(heatmap, ax=ax2)
cbar.set_label('Spearman Correlation')

# Set ticks and labels
ax2.set_xticks(dendro_idx)
ax2.set_yticks(dendro_idx)
ax2.set_xticklabels(dendro["ivl"], rotation="vertical")
ax2.set_yticklabels(dendro["ivl"])

# Show the plot
plt.tight_layout()
# plt.show()

# plt.show()

from collections import defaultdict

cluster_ids = hierarchy.fcluster(dist_linkage, 1, criterion="distance")
cluster_id_to_feature_ids = defaultdict(list)
for idx, cluster_id in enumerate(cluster_ids):
    cluster_id_to_feature_ids[cluster_id].append(idx)
selected_features = [v[0] for v in cluster_id_to_feature_ids.values()]
selected_features_names = X.columns[selected_features]

X_train_sel = X_train[selected_features_names]
X_test_sel = X_test[selected_features_names]

clf_sel = RandomForestRegressor(n_estimators=100, random_state=42)
clf_sel.fit(X_train_sel, y_train)
print(
    "Baseline accuracy on test data with features removed:"
    f" {clf_sel.score(X_test_sel, y_test):.2}"
)

fig, ax = plt.subplots(figsize=(7, 6))
plot_permutation_importance(clf_sel, X_test_sel, y_test, ax)
ax.set_title("Permutation Importances on selected subset of features\n(test set)")
ax.set_xlabel("Decrease in accuracy score")
ax.figure.tight_layout()
plt.show()

# # https://www.datacamp.com/tutorial/random-forests-classifier-python