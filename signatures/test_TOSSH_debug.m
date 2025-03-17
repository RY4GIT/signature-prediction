% Calculate signatures from Caravan dataset
% Ryoko Araki (@ry4git), 2024

% Cleaning
close all
clear all
clc

%___________________________________________________________________________________
% Add TOSSH toolbox to the path
baseDir = 'C:\Users\flipl\dev';
TOSSHDir = 'TOSSH_original\TOSSH\TOSSH_code';
addpath(genpath(fullfile(baseDir, TOSSHDir)));

% Define directories and file type
home_dir = 'G:\Shared drives\Signatures -- large scale\baseflow\RAraki';
data_dir = fullfile(home_dir, 'data');
caravan_dir = 'Caravan1.4';
attributes_dir = 'attributes';
timeseries_dir = 'timeseries';
data_type = 'csv';
caravan_data = 'hysets'; %'camels', 'hysets';

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
idx = 1;
gauge_id = cell2mat(us_gauges(idx, :).gauge_id);
disp(gauge_id); % Convert to string and display

% Load data and convert it to datetime table
file_path = fullfile(data_dir, caravan_dir, timeseries_dir,data_type, caravan_data, [gauge_id '.' data_type]);
data = readtable(file_path);
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');
data_timetable = table2timetable(data, 'RowTimes', 'date');

subset_data = data_timetable; % Just use all data in this experiment


% Prepare TOSSH imput
Q = num2cell(data.streamflow,1); %mm/day
t = num2cell(data.date,1);
P = num2cell(data.total_precipitation_sum,1);
PET = num2cell(data.potential_evaporation_sum,1);
T = num2cell(data.temperature_2m_mean,1);



%___________________________________________________________________________________
%___________________________________________________________________________________
% Signature calculation
signatures_calc_ALL = calc_All(Q, t, P, PET, T);
signatures_mcmillan_overlandflow = calc_McMillan_OverlandFlow(Q, t, P);   

% disp(signatures_calc_ALL)
disp(signatures_mcmillan_overlandflow)
%___________________________________________________________________________________
% Getting overland flow parameters 
% 
% 
% timestep = 24; % time step of precipitation array [hours] (1=hourly, 24=daily)
% min_termination = 48; % minimum termination time (time between storms) [hours]
% min_intensity_day = 4.8; % minimum intensity (per day)
% min_intensity_day_during = 4.8; % minimum timestep intensity allowed during storm event without contributing to termination time
% min_duration = 24; % minimum duration of storm [hours]
% 
% max_recessiondays = 8; % maximum number of days to allow recession after rain ends
% 
% min_intensity_hour = 2; % minimum intensity (per hour)
% min_intensity_hour_during = 0.2; % minimum timestep intensity allowed during storm event without contributing to termination time
% 
% plot_results = true;
% 
% %___________________________________________________________________________________
% % Event separation & IE SE signatures
% 
% % [IE_effect, SE_effect, IE_thresh_signif, IE_thresh, ...
% %     SE_thresh_signif, SE_thresh, SE_slope, ...
% %     Storage_thresh, Storage_thresh_signif, min_Qf_perc, ...
% %     ~, ~, fig_event] = sig_EventGraphThresholds(Q,t,P,...
% %     'min_termination', min_termination, ...
% %     'min_duration', min_duration, ...
% %     'min_intensity_day', min_intensity_day, ...
% %     'min_intensity_day_during', min_intensity_day_during, ...
% %     'max_recessiondays', max_recessiondays, ...
% %     'plot_results', plot_results);
% 
% %___________________________________________________________________________________
% % Recession signatures
% recession_length = 10;
% n_start = 0; % days to be removed after start of recession
% eps = 0.02; %  allowed increase in flow during recession period, default = 0
% filter_par = 0.925; % smoothing parameter of Lyne-Hollick filter to determine
% %      start of recession (higher = later recession start)
% [Recession_Parameters, recession_month, ~, ~, fig_recession] = ...
%     sig_RecessionAnalysis(Q, t, 'recession_length', recession_length, 'n_start', n_start, 'eps', eps, 'filter_par', filter_par, 'plot_results', true);