import pandas
import numpy
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, KFold, cross_val_predict, cross_validate
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Author: Anne Holt (@annieholt)
# Date: 2024

# import input data for random forest modeling
# in this case, dataset of hydrologic signatures and catchment attributes

# rf_data_df = pandas.read_csv("E:/SDSU_GEOG/Thesis/Data/RandomForest/sigs_attributes_master.csv")
# rf_data_df = pandas.read_csv("E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/sigs_attributes_caravan_master_v2_wet.csv")
# rf_data_df = pandas.read_csv("E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/sigs_attributes_caravan_master_v2_eco_eastern_forests.csv")
rf_data_df = pandas.read_csv("E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/sigs_attributes_caravan_master_v3.csv")
# rf_data_df = pandas.read_csv("E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/sigs_attributes_camels_master_v2.csv")

rf_data_df_dropna = rf_data_df.dropna()

# rf_data_wet = dataframe[dataframe['Percentage'] > 70]

# create a dictionary of the response variables for subsequent modeling
# keys will be hydrologic signature variable names
# include a separate predictor dataframe

# sig_list = ['EventRR', 'TotalRR', 'RR_Seasonality', 'Recession_a_Seasonality', 'AverageStorage','RecessionParameters_a',
#             'RecessionParameters_b', 'RecessionParameters_c', 'MRC_num_segments', 'First_Recession_Slope',
#             'Mid_Recession_Slope', 'Spearmans_rho', 'EventRR_TotalRR_ratio', 'VariabilityIndex', 'BaseflowRecessionK',
#             'BFI', 'BFI_90']

sig_list = ['BFI']

# either include or don't include new attributes ('geol_major_age_ma', 'non_giw_frac', 'geol_av_age_ma', 'giw_frac')
attrib_df = rf_data_df_dropna.drop(['gauge_id', 'geol_major_age_ma', 'fresh_no_giw',
                           'EventRR', 'TotalRR', 'RR_Seasonality', 'Recession_a_Seasonality', 'AverageStorage',
                           'RecessionParameters_a', 'RecessionParameters_b', 'RecessionParameters_c',
                           'MRC_num_segments', 'First_Recession_Slope', 'Mid_Recession_Slope',
                           'Spearmans_rho', 'EventRR_TotalRR_ratio', 'VariabilityIndex', 'BaseflowRecessionK',
                                    'BFI', 'BFI_90'],
                          axis=1)

# for camels dataset, drop categorical columns as well
# attrib_df = rf_data_df_dropna.drop(['gauge_id', 'geol_major_age_ma', 'non_giw_frac',
#                                     'high_prec_timing', 'low_prec_timing', 'geol_1st_class', 'glim_1st_class_frac',
#                                     'dom_land_cover', 'dom_land_cover_frac',
#                            'EventRR', 'TotalRR', 'RR_Seasonality', 'Recession_a_Seasonality', 'AverageStorage',
#                            'RecessionParameters_a', 'RecessionParameters_b', 'RecessionParameters_c',
#                            'MRC_num_segments', 'First_Recession_Slope', 'Mid_Recession_Slope',
#                            'Spearmans_rho', 'EventRR_TotalRR_ratio', 'VariabilityIndex', 'BaseflowRecessionK', 'BFI'],
#                           axis=1)

# print(attrib_df)

# empty dictionary for results
sig_dic = {}

# Loop over each response variable
for var in sig_list:
    # response variable extraction
    y = rf_data_df_dropna[var]
    # add the tuple to the dictionary with the hydrologic signature name as the key
    sig_dic[var] = y

# print(sig_dic)

# random forest modeling, optimizing number of trees
# includes 10 k fold cross validation
# test/train split of 80/20

# Assuming you have a DataFrame 'predictors_data' containing predictor variables
# and a dictionary 'response_data' containing response variables for each of the 15 variables

# Define parameter grid
param_grid = {'n_estimators': [500], 'max_features': ['log2']}
# param_grid = {'n_estimators': [10, 50, 100, 150, 200, 250, 500, 1000], 'max_features': ['log2', 'sqrt']}

# just for code testing
# param_grid = {'n_estimators': [10], 'max_features': ['log2']}

# 100 trees was generally enough to maximize accuracy but minimze computation
# (accuracy only varied about 1% with up to 1000 trees)
# accuracy varied a bit more with max_features... so letting log2 or sqrt vary for each signature
# param_grid = {'n_estimators': [100], 'max_features': ['log2', 'sqrt']}

# Initialize results dictionary
rf_results = {}

# Loop over each variable
for sig in sig_dic.keys():
    X = attrib_df  # Features
    y = sig_dic[sig]  # Target variable

    # # Split the data into training and test sets
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # instead, don't split and simply use cross validation; I want to try this since sample size is only 482

    # Perform grid search with cross-validation
    rf = RandomForestRegressor(random_state=42, n_estimators=100)
    # grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=10, scoring='r2')
    # trying mean squared error instead
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=10, scoring='neg_mean_squared_error')
    # grid_search.fit(X_train, y_train)
    grid_search.fit(X, y)

    # Store results
    rf_results[sig] = {'best_params': grid_search.best_params_, 'best_score': grid_search.best_score_,
                       'best_estimator': grid_search.best_estimator_,
                       'mean_test_score':  grid_search.cv_results_['mean_test_score']}


rf_final_results = {}
rf_performance = pandas.DataFrame()
# Based on best hyperparameters, generate final random forest models for each signature
# Loop over each variable
for sig in sig_dic.keys():
    X = attrib_df  # Features
    y = sig_dic[sig]  # Target variable

    # # Split the data into training and test sets
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    max_features = rf_results[sig]['best_params']['max_features']
    n_estimators = rf_results[sig]['best_params']['n_estimators']

    rf = RandomForestRegressor(n_estimators=n_estimators, max_features=max_features, random_state=42)
    # rf.fit(X_train, y_train)
    rf.fit(X, y)
    # print(f"R-squared on test data: {rf.score(X_test, y_test):.2f}")c
    # scoring metrics
    scoring = {'mse': 'neg_mean_squared_error', 'r2': 'r2'}

    # Perform cross-validation
    cv_results = cross_validate(rf, X, y, cv=KFold(n_splits=10, shuffle=True, random_state=42), scoring=scoring)

    # Perform cross-validation to get predictions for each fold
    y_pred_cv = cross_val_predict(rf, X, y, cv=KFold(n_splits=10, shuffle=True, random_state=42))
    # Calculate the baseline MSE
    baseline_mse = ((y - y_pred_cv) ** 2).mean()
    print(y_pred_cv)

    # Extract MSE and R^2 scores
    mse_cv_og = -cv_results['test_mse'].mean()  # Convert negative MSE to positive
    r2_cv_og = cv_results['test_r2'].mean()

    # Calculate variable importance using permutation
    perm_importance_result = permutation_importance(rf, X, y, n_repeats=10, random_state=42, scoring=scoring)

    print(perm_importance_result)

    # Extract importances and standard deviations
    importances = perm_importance_result.importances_mean
    std_deviations = perm_importance_result.importances_std

    # Calculate percent increase in MSE for each feature
    percent_increase_mse = (importances / baseline_mse) * 100
    print(percent_increase_mse)




    # # Perform 10-fold cross-validation
    # cv_scores = cross_val_score(rf, X, y, cv=KFold(n_splits=10, shuffle=True, random_state=42),
    #                             scoring='neg_mean_squared_error')

    # # mean squared error
    # y_pred = rf.predict(X_test)
    # og_mse = mean_squared_error(y_test, y_pred)
    # # print("Mean Squared Error (MSE):", mse)
    #
    # # store results
    # rf_final_results[sig] = {'mean R-squared from cross-validation': cv_scores.mean(),
    #                          'R-squared on test data': rf.score(X_test, y_test),
    #                          'mean squared error': og_mse}

    # store results
    rf_final_results[sig] = {'mean MSE from cross-validation': mse_cv_og,
                             'mean R2 from cross-validation': r2_cv_og}

    # Calculate the change in MSE for each predictor variable (by removing each variable one at a time)
    change_in_mse = []

    for attrib in range(X.shape[1]):
        # Permute values of attributes (instead of removing the attribute, which is how I initially approached this)
        X_permuted = X.copy()

        attrib_col = X_permuted.columns[attrib]

        # Convert the selected column to a list, shuffle it, and assign it back to the DataFrame
        values_list = X_permuted[attrib_col].tolist()
        numpy.random.shuffle(values_list)
        X_permuted[attrib_col] = values_list
        # print(X_permuted)

        # # Predict with the modified dataset and compute OOB mean squared error (mse_j)
        # y_pred_permuted = rf.predict(X_test_permuted)
        # mse_perm = mean_squared_error(y_test, y_pred_permuted)

        # instead using cross validation prediction
        y_pred_cv = cross_val_predict(rf, X_permuted, y, cv=KFold(n_splits=10, shuffle=True, random_state=42))

        # Calculate mean squared error (MSE)
        mse_perm = mean_squared_error(y, y_pred_cv)
        # print(mse_perm)

        # Calculate the %IncMSE for predictor variable j
        percent_inc_mse = ((mse_perm - mse_cv_og) / mse_cv_og) * 100
        change_in_mse.append(percent_inc_mse)


    # final performance results (everything)

    # Plot the change in MSE for each predictor variable
    print(change_in_mse)

    # Compute standard deviation of the differences
    std_dev_differences = numpy.std(change_in_mse)

    # Normalize change_in_mse by std_dev_differences
    normalized_change_in_mse = [x / std_dev_differences if std_dev_differences != 0 else 0 for x in change_in_mse]
    print(normalized_change_in_mse)

    sorted_idx = numpy.argsort(change_in_mse)
    sorted_change_in_mse = [change_in_mse[i] for i in sorted_idx]
    sorted_columns = X.columns[sorted_idx]
    print(sorted_change_in_mse)

    # plt.figure(figsize=(10, 6))
    # plt.barh(range(len(sorted_idx)), sorted_change_in_mse, align='center')
    # plt.yticks(range(len(sorted_idx)), sorted_columns)
    # plt.xlabel('Change in Mean Squared Error')
    # plt.title('Change in Mean Squared Error for Each Predictor Variable (Variable Removal)')
    # plt.show()

    performance_df = pandas.DataFrame({'sig': sig, 'cv_r2': r2_cv_og, 'cv_mse': mse_cv_og, 'n_trees': n_estimators,
                                     'max_features': max_features, 'variable': sorted_columns,
                                     'IncMSE': sorted_change_in_mse})
    print(performance_df)

    # Append the current iteration DataFrame to the results DataFrame
    rf_performance = rf_performance._append(performance_df, ignore_index=True)

    # # permutation importance
    # # NOTE: this is different than increase in mean squared error
    # # so later, try MSE... and decide if perturb the variable or remove it entirely
    #
    # # on test data (prob also need to check on train data to test for overfitting??)
    # var_importance = permutation_importance(rf, X_test, y_test, n_repeats=10, random_state=42)
    #
    # sorted_importances_idx = var_importance.importances_mean.argsort()
    # importances = pandas.DataFrame(
    #     var_importance.importances[sorted_importances_idx].T,
    #     columns=X.columns[sorted_importances_idx],
    # )
    # ax = importances.plot.box(vert=False, whis=10)
    # ax.set_title("Permutation Importances (test set)")
    # ax.axvline(x=0, color="k", linestyle="--")
    # ax.set_xlabel("Decrease in accuracy score")
    # ax.figure.tight_layout()
    # plt.show()

# rf_performance.to_csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/scratch/rf_performance_output.csv')
# rf_performance.to_csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_caravan_plus_wet_output.csv')
# rf_performance.to_csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_caravan_plus_eco_eastern_forests_output_v2.csv')
# rf_performance.to_csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_caravan_output_v3_BFI90.csv')
rf_performance.to_csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_camels_output_v3.csv')

print(rf_performance)
print(rf_results)
print(rf_final_results)


# Extract response variables and corresponding cross-validated accuracy scores from the results dictionary
response_variables = list(rf_results.keys())


# Create a separate plot for each response variable
for sig in response_variables:
    # Extract the cross-validated accuracy scores and corresponding hyperparameter combinations
    # for the current response variable
    scores = rf_results[sig]['mean_test_score']
    param_values = rf_results[sig]['best_params'].values()
    # param_combinations = [str(params) for params in zip(*param_values)]

    # Create a plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(len(scores)), scores, marker='o', linestyle='-')
    ax.set_xticks(range(len(scores)))
    # ax.set_xticklabels(param_combinations, rotation=45, ha='right')
    ax.set_xlabel('Parameter Combination')
    ax.set_ylabel('Accuracy Score')
    ax.set_title(f'Accuracy Scores for Response Variable {sig}')
    plt.tight_layout()
    plt.show()

print(rf_results)
