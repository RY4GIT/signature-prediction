# Potential correlations among baseflow signatures will initially be identified and summarized
# using Spearman rank correlation coefficients with the SciPy Python module and the Variance Inflation Factor (VIF)
# method using the statmodels Python module

# Author: Anne Holt (@annieholt)
# Date: 2024

from signatures.archive.calculate_sigs_camels import *
import scipy
import statsmodels
import pandas
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import calinski_harabasz_score
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from statsmodels.stats.outliers_influence import variance_inflation_factor


def run_pca(sig_df, thresh_type, thresh_value, return_type):
    """
    :param sig_df: dataframe of signatures (no extra variables, no NAs)
    :param thresh_type: threshold for choosing the number of principal components ('eigen' or 'variance')
    :param thresh_value: threshold value (either eigen value threshold, or ratio of variance explained)
    :param return_type: either return dataframe of components, or pca model ('dataframe' or 'model)
    :return: pca model or dataframe
    """

    # run PCA on signatures
    if thresh_type == 'variance':
        # set up PCA
        pca = PCA(n_components=thresh_value, svd_solver="full")
        # prepare/standardize the signature data
        standardized_df = StandardScaler().fit_transform(sig_df)
        # Calculate the components, standardized data as input
        principal_components = pca.fit_transform(np.array(standardized_df))
        # Extract into datdaframe for future clustering
        principal_df = pd.DataFrame(data=principal_components, index=sig_df.index)
        principal_df.columns = ["PC " + str(i) for i in range(1, len(principal_df.columns) + 1)]

        if return_type == 'model':
            return pca
        elif return_type == 'dataframe':
            return principal_df
        else:
            return pca

    elif thresh_type == 'eigen':
        # use n_components = None to start with the max number of components
        # set up PCA
        pca = PCA(n_components=None, svd_solver="full")
        # prepare/standardize the signature data
        standardized_df = StandardScaler().fit_transform(sig_df)
        # fit the model with data and apply the dimensionality reduction on data
        pca.fit_transform(np.array(standardized_df))

        # look at explained variance to select number of components, based on eigen value threshold
        # first create dataframe of explained variance, with index being the component
        e_var_df = pd.DataFrame(pca.explained_variance_, columns=["ExplainedVarience"])
        # then filter dataframe based one explained variance that is greater than the eigen value threshold
        e_var_df_filter = e_var_df.loc[(e_var_df['ExplainedVarience'] > thresh_value)]
        # select number of components
        n_components = len(e_var_df_filter.index)

        # then rerun pca based on determined number of components
        pca_2 = PCA(n_components=n_components, svd_solver="full")
        # Calculate the components, standardized data from above as input
        principal_components = pca_2.fit_transform(np.array(standardized_df))

        # Make it a dataframe again, with more names
        principal_df = pd.DataFrame(data=principal_components, index=sig_df.index)
        principal_df.columns = ["PC " + str(i) for i in range(1, len(principal_df.columns) + 1)]

        if return_type == 'model':
            return pca_2
        elif return_type == 'dataframe':
            return principal_df


def plot_pca_explained_variance(pca_model, out_path):
    """
    code based on following source :
    https://towardsdatascience.com/how-to-select-the-best-number-of-principal-components-for-the-dataset-287e64b14c6d'

    :param pca_model: PCA model object, resulting from run_pca() function
    :param out_path: path for saving the generated figure
    :return: None
    """
    # prepare x and y data for boxplot
    exp_var = pca_model.explained_variance_ratio_ * 100
    cum_exp_var = np.cumsum(exp_var)

    # determine number of components
    num = len(exp_var)
    print(num)

    plt.bar(range(1, num + 1), exp_var, align='center',
            label='Individual explained variance')
    plt.step(range(1, num + 1), cum_exp_var, where='mid',
             label='Cumulative explained variance', color='red')
    plt.ylabel('Explained variance percentage')
    plt.xlabel('Principal component index')

    ticks = range(1, num + 1)
    plt.xticks(ticks=ticks)
    plt.legend(loc='best')
    plt.tight_layout()

    out_name = "/pca_boxplot_variance_explained.png"
    out_full = out_path + out_name
    plt.savefig(out_full)
    # plt.show()


def create_cluster_labels(sig_df, num_groups, return_score=False):
    """
    run clustering analysis, returns cluster labels for each datapoint
    based on code from Jehn et al., 2020
    """
    np.random.seed(0)
    # set up cluster model, ward method
    agg_clust = AgglomerativeClustering(n_clusters=num_groups, linkage="ward")
    # prepare input data
    sig_df_2 = sig_df.copy(deep=True)
    sig_df_2 = StandardScaler().fit_transform(sig_df_2)
    # fit model to data
    agg_clust.fit(sig_df_2)
    # extract cluster labels
    labels = pd.DataFrame(list(agg_clust.labels_))
    labels.index = sig_df.index
    labels.columns = ["Cluster"]

    if return_score:
        return agg_clust.connectivity
    else:
        return labels


def elbow(sig_df, min_clusters, max_clusters):
    """
    creates elbow plot to determine number of clusters
    :param sig_df: input dataframe of signatures, prepped by pca
    :param min_clusters: minimum number of clusters (2 or greater)
    :param max_clusters: maximum number of clusters
    :return: None
    """
    score_dict = {}
    for num_clusters in range(min_clusters, max_clusters + 1):
        labels = create_cluster_labels(sig_df, num_clusters)
        score_dict[num_clusters] = calinski_harabasz_score(sig_df, labels)
    metrics = pd.DataFrame.from_dict(score_dict, orient="index")
    print(metrics)
    metrics.plot(legend=None)
    plt.xlabel('Number of Clusters')
    plt.ylabel('Variance Ratio Criterion')
    plt.show()


def clusters_to_loc(gauge_df, cluster_df):
    """
    Aligns cluster labels to gauge location data for future mapping
    :param gauge_df: dataframe of gauge information (latitude/longitude/id)
    :param cluster_df: dataframe of points with their associated clusters
    :return: dataframe of gaugeid/lat/long/cluster label
    """

    merge_df = pd.merge(gauge_df, cluster_df, left_index=True, right_index=True)

    return merge_df





# # visualize
#
# total_var = pca.explained_variance_ratio_.sum() * 100
#
# fig = px.scatter_3d(
#     principal_components, x=0, y=1, z=2,
#     title=f'Total Explained Variance: {total_var:.2f}%',
#     labels={'0': 'PC 1', '1': 'PC 2', '2': 'PC 3'}
# )
# fig.show()


# features = ["TotalRR", "Recession_a_Seasonality", "AverageStorage", "BFI", "BaseflowRecessionK"]
# loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
#
# fig = px.scatter(principal_components, x=0, y=1)
# for i, feature in enumerate(features):
#     fig.add_annotation(
#         ax=0, ay=0,
#         axref="x", ayref="y",
#         x=loadings[i, 0],
#         y=loadings[i, 1],
#         showarrow=True,
#         arrowsize=2,
#         arrowhead=2,
#         xanchor="right",
#         yanchor="top"
#     )
#     fig.add_annotation(
#         x=loadings[i, 0],
#         y=loadings[i, 1],
#         ax=0, ay=0,
#         xanchor="center",
#         yanchor="bottom",
#         text=feature,
#         yshift=5,
#     )
# fig.show()


# # import libraries
# import matplotlib.pyplot as plt
# import seaborn as sns
# from scipy.stats import spearmanr
# # set figure size
# plt.figure(figsize=(10,7))
# # Generate a mask to onlyshow the bottom triangle
# mask = np.triu(np.ones_like(sig_df.corr(), dtype=bool))
# # generate heatmap
# # ANNOTATE WITH CORRELATION SIGNIFICANCE... good have high correlation but not be signficant?
# sns.heatmap(sig_df.corr(), annot=True, mask=mask, vmin=-1, vmax=1, cmap='Blues')
# plt.title('Correlation Coefficient Of Predictors')
# plt.show()


# Variance Inflation Factor (VIF)
# # method using the statmodels Python module

# look for multicollinearity, when independent variables have a high correlation
# takes each feature and calculates regression with others
# greater VIF is greater correlation (above 5 is high)


# sig_vif = pandas.DataFrame
# # sig_vif["signature"] = sig_df.columns.tolist()
#
# # calculating VIF for each signature
# sig_vif["VIF"] = [variance_inflation_factor(sig_df.values, i) for i in range(len(sig_df.columns))]
#
# print(sig_vif)


# notes
# spatial autocorrelation of signatures and catchment characteristics?
# we are assuming the variables are indepedenent, but these variables are geographically related so they aren't
# closer catchments could have similar values, biasing the correlations

# type of variables? continuous? what value ranges? are there NAs?

# type of correlation...Pearsons or Spearmans Rank?...will be biased with spatial autocorrelation
# how do these work? linear relationships?

# PCA to create less correlated dataset (doesn't reduce the data, just weights?)
# use those groups, run clustering analysis on groups
