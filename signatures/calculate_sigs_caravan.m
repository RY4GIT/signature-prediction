% Calculate signatures from Caravan dataset
% Ryoko Araki (@ry4git), 2024

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
sig_cat = 'calc_All_custom';
% 'calc_All', 'calc_All_custom', 'calc_McMillan_OverlandFlow', 'calc_McMillan_Groundwater',
% 'calc_Addor', 'calc_Sawicz', 'calc_Euser',  'calc_BasicSet'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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
caravan_data = 'hysets';

currentDate = datestr(now, 'yyyymmdd');
out_dir = fullfile(home_dir, 'out', 'signatures', ['caravan_', caravan_data, '_', currentDate]);
out_filename = ['out_' sig_cat '.csv'];
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

% Parameter config
config_OF = readtable('calculate_sigs_config_overlandflow.csv');
config_recession = readtable('calculate_sigs_config_recession.csv');

plot_results = false;

%___________________________________________________________________________________
% Prepare parallel pool
%
% Specify the number of workers
numWorkers = 12;  % Adjust based on your system capabilities

% Set up the parallel pool
pool = gcp('nocreate');
if isempty(pool)
    parpool(numWorkers);  % Start a parallel pool
end

% Initialize the cell array for results
resultsCell = cell(numGauges, 1);

% Progress update setup
fprintf("Starting processing ... %s dataset", caravan_data);

%___________________________________________________________________________________
% Loop through each gauge in us_gauges and collect data
parfor idx = 1:numGauges
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
        Q = num2cell(data.streamflow,1); %mm/day
        t = num2cell(data.date,1);
        P = num2cell(data.total_precipitation_sum,1);
        PET = num2cell(data.potential_evaporation_sum,1);
        T = num2cell(data.temperature_2m_mean,1);
        
        %___________________________________________________________________________________
        % Get parameters
        
        if strcmp(sig_cat,'calc_All_custom')
            
            try
                % Overland flow
                parts = split(gauge_id, '_');
                gauge_code = parts{2};
                ws_code = str2double(gauge_code(1:2));
                OF_param = config_OF(config_OF.ws_code == ws_code, :);
                
                % Recession
                p95 = prctile(data.streamflow, 95);
                if (p95 < 1)
                    recession_param = config_recession(string(config_recession.flow) == {'low'}, :);
                else
                    recession_param = config_recession(string(config_recession.flow) == {'normal'}, :);
                end
                
            catch ME
                fprintf('Error at index %d: %s\n', idx, ME.message);
            end
        end
        
        %___________________________________________________________________________________
        % Signature calculation
        switch sig_cat
            case 'calc_All'
                signatures = calc_All(Q, t, P, PET, T);
            case 'calc_All_custom'
                try
                    signatures = calc_All_custom(Q, t, P, PET, T,...
                        'min_termination', OF_param.min_termination, ...
                        'min_duration', OF_param. min_duration, ...
                        'min_intensity_day', OF_param.min_intensity_day, ...
                        'min_intensity_day_during', OF_param.min_intensity_day_during, ...
                        'max_recessiondays', OF_param.max_recessiondays, ...
                        'recession_length', recession_param.recession_length, ...
                        'eps', recession_param.eps, ...
                        'plot_results', plot_results ...
                        );
                catch ME
                    fprintf('Error at index %d: %s\n', idx, ME.message);
                    signatures = calc_All(Q, t, P, PET, T);
                end
            case 'calc_McMillan_Groundwater'
                signatures = calc_McMillan_Groundwater(Q, t, P, PET);
            case 'calc_McMillan_OverlandFlow'
                signatures = calc_McMillan_OverlandFlow(Q, t, P);
            case 'calc_Addor'
                signatures = calc_Addor(Q, t, P);
            case 'calc_BasicSet'
                signatures = calc_BasicSet(Q, t);
            case 'calc_Euser'
                signatures = calc_Euser(Q, t);
            case 'calc_Sawicz'
                signatures = calc_Sawicz(Q, t, P, T);
            otherwise
                warning('Unexpected signature category');
        end
        
        % Make table
        signatures = struct2table(signatures);
%         signatures.gauge_id = gauge_id; % this somehow doesn't work when
%         doing vertcat
        
        % Store the results in the Composite variable
        resultsCell{idx} = signatures;
        
    catch ME
        fprintf('Error at index %d: %s\n', idx, ME.message);
    end
end

% Combine all results into one table after the loop
results = vertcat(resultsCell{:});
results.gauge_id = us_gauges.gauge_id(1:numGauges);

if contains(sig_cat, 'calc_All')
    % remove FDC to save space
    results.FDC = [];
    results.FDC_error_str = [];
end

% Save the table to a CSV file
writetable(results, fullfile(out_dir, out_filename), 'WriteVariableNames', true);
fprintf('Finished the analysis. Results are saved to %s\n', fullfile(out_dir, out_filename));
fprintf('Total processing time: %.2f seconds\n', toc(totalTimer));

diary off;