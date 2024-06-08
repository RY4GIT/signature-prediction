% Calculate signatures from Caravan dataset
% Ryoko Araki (@ry4git), 2024

% Cleaning
close all
clear all
delete(gcp('nocreate'))
clc

%___________________________________________________________________________________
% Add TOSSH toolbox to the path
baseDir = 'C:\Users\flipl\dev';
TOSSHDir = 'TOSSH\TOSSH_code';
addpath(genpath(fullfile(baseDir, TOSSHDir)));

% Define directories and file type
home_dir = 'G:\Shared drives\Signatures -- large scale\baseflow\RAraki';
data_dir = fullfile(home_dir, 'data');
caravan_dir = 'Caravan1.4';
attributes_dir = 'attributes';
timeseries_dir = 'timeseries';
data_type = 'csv';
caravan_data = 'camels';

currentDate = datestr(now, 'yyyymmdd');
out_dir = fullfile(home_dir, 'out', 'signatures', ['caravan_', caravan_data, '_deepdive_', currentDate]);
if ~exist(out_dir, 'dir')
    mkdir(out_dir);  % This will create the directory and any necessary subdirectories
    fprintf('Directory created: %s\n', out_dir);
else
    fprintf('Directory already exists: %s\n', out_dir);
end

%___________________________________________________________________________________
% Read metadata
attrs_geo = readtable(fullfile(data_dir, caravan_dir, attributes_dir, caravan_data, ['attributes_other_' caravan_data '.' data_type]));
attrs_geo_names = attrs_geo.Properties.VariableNames;
% disp(head(attrs_geo));

% Filter data for US gauges
us_gauges = attrs_geo(strcmp(attrs_geo.country, 'United States of America'), :);
% disp(head(us_gauges));

% Number of gauges
numGauges = height(us_gauges);

%___________________________________________________________________________________
% Data preparation
% Specify the gauge id
gauge_id = 'camels_01435000';

% Load data and convert it to datetime table
file_path = fullfile(data_dir, caravan_dir, timeseries_dir,data_type, caravan_data, [gauge_id '.' data_type]);
data = readtable(file_path);
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');
data_timetable = table2timetable(data, 'RowTimes', 'date');

% Subset data_timetable to 2010-2012
start_year = 2012;
end_year = start_year + 1;
TR = timerange(datetime(start_year, 10, 1),datetime(end_year, 9,30));
subset_data = data_timetable(TR, :);

% Prepare TOSSH imput
Q = subset_data.streamflow; %mm/day
t = subset_data.date;
P = subset_data.total_precipitation_sum;
PET = subset_data.potential_evaporation_sum;
T = subset_data.temperature_2m_mean;

%___________________________________________________________________________________
%___________________________________________________________________________________
% Signature calculation

%___________________________________________________________________________________
% Event separation for overland flow signature calculation
% https://github.com/TOSSHtoolbox/TOSSH/blob/master/TOSSH_code/utility_functions/util_EventSeparation.m

timestep = 24; % time step of precipitation array [hours] (1=hourly, 24=daily)

min_termination = 72; % minimum termination time (time between storms) [hours]
min_duration = 24; % minimum duration of storm [hours]
min_intensity_day = 10; % minimum intensity (per day)
min_intensity_day_during = 4.8; % minimum timestep intensity allowed during storm event without contributing to termination time
max_recessiondays = 6; % maximum number of days to allow recession after rain ends

min_intensity_hour = 2; % minimum intensity (per hour)
min_intensity_hour_during = 0.2; % minimum timestep intensity allowed during storm event without contributing to termination time
plot_results = true;

[stormarray, ~, ~, fig_storm] = util_EventSeparation(...
    datenum(t), P, timestep, min_termination, min_duration, ...
    min_intensity_hour, min_intensity_day, ...
    min_intensity_hour_during, min_intensity_day_during, ...
    max_recessiondays, false);

[IE_effect, SE_effect, IE_thresh_signif, IE_thresh, ...
    SE_thresh_signif, SE_thresh, SE_slope, ...
    Storage_thresh, Storage_thresh_signif, min_Qf_perc, ...
    ~, ~, fig_event] = sig_EventGraphThresholds(Q,t,P,...
    'min_termination', min_termination, ...
    'min_duration', min_duration, ...
    'min_intensity_day', min_intensity_day, ...
    'min_intensity_day_during', min_intensity_day_during, ...
    'max_recessiondays', max_recessiondays, ...
    'plot_results', plot_results);

% recession_length = 5;
% n_start = 1;
% eps = 0;
% filter_par = 0.925;
% [Recession_Parameters, recession_month, ~, ~, fig_recession] = ...
%     sig_RecessionAnalysis(Q, t, 'recession_length', recession_length, 'n_start', n_start, 'eps', eps, 'filter_par', filter_par, 'plot_results', true);

stormarray_datetime = t(stormarray);