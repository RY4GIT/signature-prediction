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
% Add TOSSH toolbox to the path
baseDir = 'C:\Users\flipl\dev'; % 'G:\Araki\proj' on lab computer
TOSSHDir = 'TOSSH\TOSSH_code';
addpath(genpath(fullfile(baseDir, TOSSHDir)));

% Define directories and file type
cloud_dir = 'G:\Shared drives\Signatures -- large scale\baseflow\RAraki'; % 'G:\Araki' on lab computer
data_dir = 'D:\data';
camelsh_dir = 'CAMELSH';
gages2_dir = 'GAGES2_concat';
data_type = 'csv';

ds_name = 'gages2';


currentDate = datestr(now, 'yyyymmdd');
out_dir = fullfile(cloud_dir, 'out', 'signatures', ['Wu_sigs_', currentDate]);
out_filename = ['out_sigEvent_', ds_name, '.csv'];
if ~exist(out_dir, 'dir')
    mkdir(out_dir);  % This will create the directory and any necessary subdirectories
    fprintf('Directory created: %s\n', out_dir);
else
    fprintf('Directory already exists: %s\n', out_dir);
end

%___________________________________________________________________________________

% Get list of files in the directory
files = dir(fullfile(data_dir, gages2_dir, 'gages2_*.csv'));

% Extract gauge IDs from filenames
gauge_ids = cell(length(files), 1);
for i = 1:length(files)
    % Get filename without extension
    [~, filename] = fileparts(files(i).name);
    % Extract gauge ID by removing 'gages2_' prefix
    gauge_ids{i} = erase(filename, 'gages2_');
end

%___________________________________________________________________________________

% Number of gauges
numGauges = height(gauge_ids);

% Parameter config
config_OF = readtable('config_overlandflow.csv');
plot_results = false;

%
% %___________________________________________________________________________________
% % Prepare parallel pool
%
% Specify the number of workers
numWorkers = 6;  % Adjust based on your system capabilities

% Set up the parallel pool
pool = gcp('nocreate');
if isempty(pool)
    parpool(numWorkers);  % Start a parallel pool
end

% Progress update setup
fprintf("Starting processing hourly CAMELS dataset");

%___________________________________________________________________________________
% Loop through each gauge in us_gauges and collect data
for i = 1:numGauges
    try
        % Get the gauge id
        gauge_id = cell2mat(gauge_ids(i, :));
        gauge_num = gauge_id;
        fprintf("Currently processing %s\n", gauge_id)
        
        %___________________________________________________________________________________
        % Data preparation
        % Load data and convert it to datetime table
        file_path = fullfile(data_dir, gages2_dir, ['gages2_' gauge_id '.' data_type]);
        data = readtable(file_path);
        data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');
        data_timetable = table2timetable(data, 'RowTimes', 'date');

        % Load hourly fraction data
        file_path = fullfile(data_dir, camelsh_dir, "timeseries_max_hourly_frac", [gauge_num '.' data_type]);
        maxP_hr_frac = readtable(file_path);
        maxP_hr_frac.DateTime = datetime(maxP_hr_frac.DateTime, 'InputFormat', 'yyyy-MM-dd');
        maxP_hr_frac_timetable = table2timetable(maxP_hr_frac, 'RowTimes', 'DateTime');

        % Subset hourly data to overlap with daily data time range
        time_start = maxP_hr_frac_timetable.Properties.RowTimes(1);
        time_end = data_timetable.Properties.RowTimes(end);
        maxP_hr_frac_tt = maxP_hr_frac_timetable(timerange(time_start, time_end), :);
        data_tt = data_timetable(timerange(time_start, time_end), :);

        % Synchronize the timetables using NLDAS as temporal baseline
        sync_data = synchronize(data_tt, maxP_hr_frac_tt, 'union', 'fillwithmissing');

        % Prepare TOSSH imput
        Q = num2cell(sync_data.streamflow_mmd,1); %mm/day
        t = num2cell(sync_data.date,1);
        P = num2cell(sync_data.total_precipitation_sum_mm,1);
        P_hrfrac = num2cell(sync_data.max_hourly_frac, 1);  % Use hourly fraction
        PET = num2cell(sync_data.potential_evaporation_sum_mm,1);
        T = num2cell(sync_data.temperature_mean_degc,1);


        %___________________________________________________________________________________
        % Get parameters

        % Overland flow
        ws_code = str2double(gauge_num(1:2));
        OF_param = config_OF(config_OF.ws_code == ws_code, :);

        %___________________________________________________________________________________
        % Event separation & IE SE signatures
        R_Pvol_RC = NaN(size(Q,1),1);
        R_Pint_RC = NaN(size(Q,1),1);
        n_events = NaN(size(Q,1),1);
        % OF_error_str = strings(size(Q,1),1);

        [~,~,~,~, ...
            ~,~,~,~, ...
            ~,~,R_Pvol_RC, R_Pint_RC,n_events,~,~] ...
            = sig_EventGraphThresholds_hourlyRain(Q{1},t{1},P{1},P_hrfrac{1},...
            'min_termination', OF_param.min_termination, ...
            'min_duration', OF_param.min_duration, ...
            'min_intensity_day', OF_param.min_intensity_day, ...
            'min_intensity_day_during', OF_param.min_intensity_day_during, ...
            'max_recessiondays', OF_param.max_recessiondays, ...
            'plot_results',plot_results);

        results = [];
        results.gauge_id = ['gages2_' num2str(gauge_id)];
        results.R_Pvol_RC = R_Pvol_RC;
        results.R_Pint_RC = R_Pint_RC;
        results.n_events = n_events;
        % results.OF_error_str = OF_error_str;

        % Make table
        signatures = struct2table(results);
        %         signatures.gauge_id = gauge_id; % this somehow doesn't work when
        %         doing vertcat

        % Store the results in the Composite variable
        resultsCell{i} = signatures;

    catch ME
        fprintf('Error at index %d: %s\n', i, ME.message);

        % Create an empty output
        fieldNames = {
            'R_Pvol_RC', 'R_Pint_RC', 'n_events'
            };

        % Initialize the struct dynamically
        signatures = struct();
        for i = 1:numel(fieldNames)
            if contains(fieldNames{i}, '_error_str')  % If field is an error string field
                signatures.(fieldNames{i}) = "";         % Assign empty string
            elseif strcmp(fieldNames{i}, 'EventGraphThresholds') % Ensure EventGraphThresholds is an array of length 10
                signatures.(fieldNames{i}) = NaN(1, 10);
            elseif strcmp(fieldNames{i}, 'MRC_SlopeChanges') % Ensure MRC_SlopeChanges is an array of length 2
                signatures.(fieldNames{i}) = {NaN(1, 2), NaN(1,2)};
            elseif strcmp(fieldNames{i}, 'PQ_Curve') % Ensure MRC_SlopeChanges is an array of length 2
                signatures.(fieldNames{i}) = NaN(1, 4);
                % elseif strcmp(fieldNames{i}, 'RecessionParameters') % Ensure
                % MRC_SlopeChanges is an array of length 2 ... when the first
                % is for entire (non-individual) flow duration curve
                %     signatures.(fieldNames{i}) = NaN(1, 2);
            elseif strcmp(fieldNames{i}, 'SeasonalTranslation') % Ensure MRC_SlopeChanges is an array of length 2
                signatures.(fieldNames{i}) = NaN(1, 2);
            elseif strcmp(fieldNames{i}, 'StorageFraction') % Ensure MRC_SlopeChanges is an array of length 2
                signatures.(fieldNames{i}) = NaN(1, 3);
            else
                signatures.(fieldNames{i}) = NaN(1, 1);        % Assign NaN for numerical values
            end
        end
        signatures.gauge_id = gauge_id;
        % Make table
        signatures = struct2table(signatures);
        resultsCell{i} = signatures;

    end
end

% Combine all results into one table after the loop
% First convert gauge_id to cell array to avoid dimension mismatch
for i = 1:length(resultsCell)
    if ~isempty(resultsCell{i})
        resultsCell{i}.gauge_id = {resultsCell{i}.gauge_id};
    end
end
results = vertcat(resultsCell{:});

% Save the table to a CSV file
writetable(results, fullfile(out_dir, out_filename), 'WriteVariableNames', true);
fprintf('Finished the analysis. Results are saved to %s\n', fullfile(out_dir, out_filename));
fprintf('Total processing time: %.2f seconds\n', toc(totalTimer));

diary off;