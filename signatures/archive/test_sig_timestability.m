% Calculate signatures from Caravan dataset
% Ryoko Araki (@ry4git), 2024

% Initialize and clean up
close all; clear all; clc;

% Directory setup
baseDir = 'C:\Users\flipl\dev';
TOSSHDir = 'TOSSH\TOSSH_code';
addpath(genpath(fullfile(baseDir, TOSSHDir)));

home_dir = 'G:\Shared drives\Signatures -- large scale\baseflow\RAraki';
data_dir = fullfile(home_dir, 'data');
caravan_dir = 'Caravan1.4';
attributes_dir = 'attributes';
timeseries_dir = 'timeseries';
data_type = 'csv';
caravan_data = 'camels';

% Output directory
currentDate = datestr(now, 'yyyymmdd');
out_dir = fullfile(home_dir, 'out', 'signatures', ['caravan_', caravan_data, '_timestability_', currentDate]);
if ~exist(out_dir, 'dir')
    mkdir(out_dir);
end

%___________________________________________________________________________________
% Read metadata
attrs_geo = readtable(fullfile(data_dir, caravan_dir, attributes_dir, caravan_data, ['attributes_other_' caravan_data '.' data_type]));
attrs_geo_names = attrs_geo.Properties.VariableNames;

% Filter data for US gauges
us_gauges = attrs_geo(strcmp(attrs_geo.country, 'United States of America'), :);

% Number of gauges
numGauges = height(us_gauges);

%___________________________________________________________________________________
% Prepare parallel pool

% % % Specify the number of workers
numWorkers = 12;  % Adjust based on your system capabilities

% Set up the parallel pool
pool = gcp('nocreate');
if isempty(pool)
    parpool(numWorkers);  % Start a parallel pool
end

%___________________________________________________________________________________
% Year setup
start_year = 1988;
num_years = 30;

%___________________________________________________________________________________
% Loop through each gauge in us_gauges and collect data
parfor idx = 1:numGauges
    try
        %___________________________________________________________________________________
        % Gauge setup
        % Get the gauge id
        gauge_id = cell2mat(us_gauges(idx, :).gauge_id);
        fprintf("Currently processing %s\n", gauge_id)
        out_filename = ['out_calc_ALL_', gauge_id, '.csv'];
        
        % Initialize the cell array for results
        resultsCell = cell(num_years, 1);
        
        %___________________________________________________________________________________
        % Loop over each year and calculate signatures
        for year = 1:num_years
            end_year = start_year + year;
            try
                % Load data
                file_path = fullfile(data_dir, caravan_dir, timeseries_dir,data_type, caravan_data, [gauge_id '.' data_type]);
                data = readtable(file_path);
                data.date = datetime(data.date, 'InputFormat', 'yyyy-MM-dd');
                data_timetable = table2timetable(data, 'RowTimes', 'date');
                
                % Subset data_timetable to the specific year
                TR = timerange(datetime(start_year, 10, 1),datetime(end_year, 9,30));
                subset_data = data_timetable(TR, :);
                
                % Data preparation (example placeholders)
                Q = num2cell(subset_data.streamflow,1); %mm/day
                t = num2cell(subset_data.date,1);
                P = num2cell(subset_data.total_precipitation_sum,1);
                PET = num2cell(subset_data.potential_evaporation_sum,1);
                T = num2cell(subset_data.temperature_2m_mean,1);
                plot_results = false;
                
                % Signature calculation
                signatures = calc_All(Q, t, P, PET, T);
                signatureTable = struct2table(signatures);
                signatureTable.start_year = start_year;
                signatureTable.end_year = end_year;
                signatureTable.gauge_id = gauge_id;
                
                % Store the results in the Composite variable
                resultsCell{year} = signatureTable;
                
            catch ME
                fprintf('Error processing year %d: %s\n', end_year, ME.message);
            end
        end
        
        %___________________________________________________________________________________
        % Concat results from multiple years
        results = vertcat(resultsCell{:});
        results.FDC = [];
        results.FDC_error_str = [];
        
        % Save results to a CSV file
        writetable(results, fullfile(out_dir, out_filename), 'WriteVariableNames', true);
        fprintf('Results saved to %s\n', fullfile(out_dir, out_filename));
        
    catch ME
        fprintf('Error processing gauge %s: %s\n', gauge_id, ME.message);
    end
    
end
