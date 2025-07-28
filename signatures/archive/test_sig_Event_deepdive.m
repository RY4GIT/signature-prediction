% Calculate signatures from Caravan dataset
% Ryoko Araki (@ry4git), 2024

% Cleaning
close all
clear all
clc

%___________________________________________________________________________________
% Add TOSSH toolbox to the path
baseDir = 'C:\Users\flipl\dev';
TOSSHDir = 'TOSSH\TOSSH_code';
addpath(genpath(fullfile(baseDir, TOSSHDir)));

% Define directories and file type
home_dir = 'G:\Shared drives\Signatures -- large scale\baseflow\RAraki';
d_dir = 'D:\';
data_dir = fullfile(d_dir, 'data');
caravan_dir = 'Caravan1.4';
attributes_dir = 'attributes';
timeseries_dir = 'timeseries';
data_type = 'csv';
caravan_data = 'camels'; %'camels', 'hysets';

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
gauge_id = 'camels_12025000';

% IE_thresh is ridiculously high for 
% hysets_07156100
% hysets_09387300
% hysets_09415850
% hysets_09518500
% hysets_09520280
% hysets_10257800
% hysets_10261800
% hysets_10264590
% hysets_11413517

% SE_thresh is ridiculously high for 
% hysets_07156100
% hysets_09415850
% hysets_09518500
% hysets_09520280

% SE_slope is ridiculously high for 
% hysets_0208423100	
% hysets_10250600	

% Total RR > 5
% hysets_0208423100
% hysets_0208735012	
% hysets_02110704	
% hysets_02231254	
% hysets_03401428	
% hysets_03401450	
% hysets_06400497	

% Load data and convert it to datetime table
file_path = fullfile(data_dir, caravan_dir, timeseries_dir,data_type, caravan_data, [gauge_id '.' data_type]);
data = readtable(file_path);
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');
data_timetable = table2timetable(data, 'RowTimes', 'date');

subset_data = data_timetable; % Just use all data in this experiment

% Prepare TOSSH input
Q = subset_data.streamflow; %mm/day
t = subset_data.date;
P = subset_data.total_precipitation_sum;
PET = subset_data.potential_evaporation_sum;
T = subset_data.temperature_2m_mean;


%___________________________________________________________________________________
%___________________________________________________________________________________
% Signature calculation
                
%___________________________________________________________________________________
% Getting overland flow parameters 

config_OF = readtable('config_overlandflow.csv');

parts = split(gauge_id, '_');
gauge_code = parts{2};
ws_code = str2double(gauge_code(1:2));
OF_param = config_OF(config_OF.ws_code == ws_code, :);


timestep = 24; % time step of precipitation array [hours] (1=hourly, 24=daily)

min_termination = OF_param.min_termination; % 48; % minimum termination time (time between storms) [hours]

min_intensity_day = OF_param.min_intensity_day; % 4.8; % minimum intensity (per day)
min_intensity_day_during = OF_param.min_intensity_day_during; % 4.8; % minimum timestep intensity allowed during storm event without contributing to termination time

min_duration = OF_param.min_duration; % 24; % minimum duration of storm [hours]

max_recessiondays = OF_param.max_recessiondays; % 8; % maximum number of days to allow recession after rain ends

min_intensity_hour = 2; % minimum intensity (per hour)
min_intensity_hour_during = 0.2; % minimum timestep intensity allowed during storm event without contributing to termination time

plot_results = true;

%___________________________________________________________________________________
% Event separation & IE SE signatures

[IE_effect, SE_effect, IE_thresh_signif, IE_thresh, ...
    SE_thresh_signif, SE_thresh, SE_slope, ...
    Storage_thresh, Storage_thresh_signif, min_Qf_perc, ...
     R_Pvol_RC, R_Pint_RC, fig_event] = sig_EventGraphThresholds(Q,t,P,...
    'min_termination', min_termination, ...
    'min_duration', min_duration, ...
    'min_intensity_day', min_intensity_day, ...
    'min_intensity_day_during', min_intensity_day_during, ...
    'max_recessiondays', max_recessiondays, ...
    'plot_results', plot_results);

disp(R_Pvol_RC)
disp(R_Pint_RC)

%___________________________________________________________________________________
% Recession signatures
recession_length = 10;
n_start = 0; % days to be removed after start of recession
eps = 0.02; %  allowed increase in flow during recession period, default = 0
filter_par = 0.925; % smoothing parameter of Lyne-Hollick filter to determine
%      start of recession (higher = later recession start)
[Recession_Parameters, recession_month, ~, ~, fig_recession] = ...
    sig_RecessionAnalysis(Q, t, 'recession_length', recession_length, 'n_start', n_start, 'eps', eps, 'filter_par', filter_par, 'plot_results', true);
