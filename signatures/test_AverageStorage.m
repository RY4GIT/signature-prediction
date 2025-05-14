% Calculate signatures from Caravan dataset
% Test the recession parameters used in Large Scale Signature Paper
% (McMillan et al., 2021)

% The workflow uses calc_McMillan_Groundwater and only specifies
% start_water_year for the US
% https://github.com/SebastianGnann/LargeScaleSigs/blob/master/workflow_CalculateSignatures.m

% Therefore, it is likely that Sebastian used the default parameters in the
% calc_McMillan_Groundwater
% https://github.com/TOSSHtoolbox/TOSSH/blob/master/TOSSH_code/calculation_functions/calc_McMillan_Groundwater.m
% which is,
% addParameter(ip, 'recession_length', 5, @isnumeric) % length of recessions to find (days)
% addParameter(ip, 'n_start', 1, @isnumeric) % time after peak to start recession (days)
% addParameter(ip, 'eps', 0, @isnumeric) % allowed increase in flow during recession period

% Try this instead of tuned parameters in my code for calculating
% AverageStorage


% Ryoko's tuned parameters are
% flow	recession_length	n_start	eps	filter_par
% normal	5	0	0.08	0.925
% low	10	0	0.02	0.925

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

currentDate = datestr(now, 'yyyymmdd');
out_dir = fullfile(home_dir, 'out', 'signatures', ['caravan_', caravan_data, '_AvgStr_', currentDate]);
out_filename = ['out_AvgStr.csv'];
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
% Initialize the cell array for results
resultsCell = cell(numGauges, 1);
AverageStorage = NaN(numGauges, 1);
AverageStorage_error_str = strings(numGauges, 1);
flow_condition = strings(numGauges, 1);

% Parameter setup
start_water_year = 10;
recession_length = 5; %  min. length of recession segments [days], default = 5
n_start = 1; % days to be removed after start of recession
eps = 0; %  allowed increase in flow during recession period
plot_results = false;

% Progress update setup
fprintf("Starting processing ... %s dataset", caravan_data);

for idx = 1:numGauges
    try
        % Get the gauge id
        gauge_id = cell2mat(us_gauges(idx, :).gauge_id);
        fprintf("Currently processing %s\n", gauge_id)

        %___________________________________________________________________________________
        % Data preparation
        % Load data and convert it to datetime table
        file_path = fullfile(data_dir, caravan_dir, timeseries_dir,data_type, caravan_data, [gauge_id '.' data_type]);
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

        [AverageStorage(idx),~,AverageStorage_error_str(idx)] = ...
            sig_StorageFromBaseflow(Q, t, P,PET,'start_water_year',start_water_year,'plot_results',plot_results,'recession_length',recession_length,'n_start',n_start,'eps',eps);

        % Check high/low flow in config_recession
        % Recession
        p95 = prctile(Q, 95);
        if (p95 < 1)
            flow_condition(idx) = "low";
        else
            flow_condition(idx) = "high";
        end

    catch ME
        fprintf('Error at index %d: %s\n', idx, ME.message);
    end
end

% Debug information and create table with verified sizes
fprintf('Size checks before creating table:\n');
fprintf('gauge_ids size: %d\n', length(us_gauges.gauge_id(1:numGauges)));
fprintf('AverageStorage size: %d\n', length(AverageStorage));
fprintf('AverageStorage_error_str size: %d\n', length(AverageStorage_error_str));

% Create a table from the results with proper initialization
gauge_ids = us_gauges.gauge_id(1:numGauges);
results_table = table(gauge_ids, AverageStorage, AverageStorage_error_str, flow_condition, ...
    'VariableNames', {'gauge_id', 'AverageStorage', 'AverageStorage_error_str', 'flow_condition'});

% Save the table to a CSV file
writetable(results_table, fullfile(out_dir, out_filename), 'WriteVariableNames', true);
fprintf('Finished the analysis. Results are saved to %s\n', fullfile(out_dir, out_filename));

diary off;