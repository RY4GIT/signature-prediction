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
caravan_data = 'hysets'; %'camels', 'hysets';

%___________________________________________________________________________________
% Read metadata
attrs_geo = readtable(fullfile(data_dir, caravan_dir, attributes_dir, caravan_data, ['attributes_other_' caravan_data '.' data_type]));
attrs_geo_names = attrs_geo.Properties.VariableNames;
% disp(head(attrs_geo));

% Filter data for US gauges
us_gauges = attrs_geo(strcmp(attrs_geo.country, 'United States of America'), :);
% disp(head(us_gauges));

% Progress update setup
fprintf("Starting processing ... %s dataset", caravan_data);


gauge_id = "hysets_01010000"; % hysets_13135500

fprintf("Currently processing %s\n", gauge_id)

%___________________________________________________________________________________
% Data preparation
% Load data and convert it to datetime table
file_path = fullfile(data_dir, caravan_dir, timeseries_dir,data_type, caravan_data, char(gauge_id + "." + data_type));
data = readtable(file_path);
data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');
data_timetable = table2timetable(data, 'RowTimes', 'date');
%     disp(head(data_timetable));

% Prepare TOSSH imput
Q = data.streamflow; %mm/day
t = data.date;
P = data.total_precipitation_sum;
PET = data.potential_evaporation_sum;
T = data.temperature_2m_mean;

%___________________________________________________________________________________
%___________________________________________________________________________________
% Signature calculation
[BFI,~,BFI_error_str] = sig_BFI(Q,t, "plot_results", true);
