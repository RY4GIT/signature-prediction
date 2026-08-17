% Calculate signatures from Caravan dataset
% Ryoko Araki (@ry4git), 2024
% Current directly should be ..\signature-prediction\signatures\.

% Cleaning
close all
clear all
delete(gcp('nocreate'))
clc

% Start the total runtime timer
totalTimer = tic;
diary('log.txt');

%___________________________________________________________________________________
% CHANGE HERE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Declare signature function/category to use
sig_cat = 'calc_All_custom_shortlist';
% 'calc_All', 'calc_All_custom', 'calc_All_custom_shortlist', 'calc_McMillan_OverlandFlow', 'calc_McMillan_Groundwater',
% 'calc_Addor', 'calc_Sawicz', 'calc_Euser',  'calc_BasicSet'

% Choose which Caravan gaguges to run: 'hysets' or 'camels'
caravan_data = 'camels';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%___________________________________________________________________________________
% Add TOSSH toolbox to the path
baseDir = 'C:\Users\flipl\dev'; % 'G:\Araki\proj' on lab computer
TOSSHDir = 'TOSSH\TOSSH_code';
addpath(genpath(fullfile(baseDir, TOSSHDir)));

% Define directories and file type
cloud_dir = 'G:\Shared drives\Signatures -- large scale\baseflow\RAraki'; % 'G:\Araki' on lab computer
data_dir = 'E:\data';
caravan_dir = 'Caravan1.5';
attributes_dir = 'attributes';
timeseries_dir = 'timeseries';
data_type = 'csv';


%___________________________________________________________________________________
% Parameter config
config_OF = readtable('config_overlandflow.csv');
config_recession = readtable('config_recession.csv');
plot_results = true;
gauge_id = "camels_06353000";

%___________________________________________________________________________________
fprintf("Currently processing %s\n", gauge_id)

%___________________________________________________________________________________
% Data preparation
% Load data and convert it to datetime table
file_path = fullfile(data_dir, caravan_dir, timeseries_dir, data_type, caravan_data, [char(gauge_id) '.' data_type]);
data = readtable(file_path);
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');
data_timetable = table2timetable(data, 'RowTimes', 'date');
%     disp(head(data_timetable));

% Prepare TOSSH imput
Q = num2cell(data.streamflow,1); %mm/day
t = num2cell(data.date,1);
P = num2cell(data.total_precipitation_sum,1);
PET = num2cell(data.potential_evaporation_sum_FAO_PENMAN_MONTEITH,1);
T = num2cell(data.temperature_2m_mean,1);

%___________________________________________________________________________________
if strcmp(sig_cat,'calc_All_custom') || strcmp(sig_cat,'calc_All_custom_shortlist')
    % Overland flow
    parts = split(gauge_id, '_');
    gauge_code = parts{2};
    ws_code = str2double(gauge_code(1:2));
    OF_param = config_OF(config_OF.ws_code == ws_code, :);

    % Recession
    p95 = prctile(data.streamflow, 95);
    if (p95 < 1)
        recession_param = config_recession(string(config_recession.flow) == "low", :);
    else
        recession_param = config_recession(string(config_recession.flow) == "normal", :);
    end
    fprintf('p95 = %.4f mm/d, recession flow class = %s\n', p95, recession_param.flow{1});
end

%___________________________________________________________________________________
% Signature calculation
% Recession a Seasonality (custom recession parameters)
i=1;
eps = recession_param.eps; %median(Q{i}, 'omitnan') * 0.01;
fprintf('eps = %.6f\n', eps);

[Recession_a_Seasonality, ~, Recession_a_Seasonality_error_str] = ...
    sig_SeasonalVarRecessions(Q{i}, t{i}, ...
    'recession_length', recession_param.recession_length, ...
    'n_start', recession_param.n_start, ...
    'eps', eps, ...
    'plot_results', plot_results);

fprintf('Recession_a_Seasonality = %.6f\n', Recession_a_Seasonality);
if strlength(string(Recession_a_Seasonality_error_str)) > 0
    fprintf('error_str: %s\n', string(Recession_a_Seasonality_error_str));
end
fprintf('Total processing time: %.2f seconds\n', toc(totalTimer));

[Recession_Parameters, recession_month, error_flag, error_str, fig_handles] = ...
    sig_RecessionAnalysis(Q{i}, t{i}, 'recession_length', recession_param.recession_length, ...
    'n_start', recession_param.n_start, ...
    'eps', eps, ...
    'plot_results', plot_results);
fprintf('Recession parameters%.6f\n', Recession_Parameters);
if strlength(string(error_str)) > 0
    fprintf('error_str: %s\n', string(error_str));
end
fprintf('Total processing time: %.2f seconds\n', toc(totalTimer));


% recession_month is your vector of month values (1-12)

% Count of recessions per month
month_counts = histcounts(recession_month, 0.5:1:12.5);
month_labels = 1:12;

table(month_labels', month_counts', 'VariableNames', {'Month','Count'})