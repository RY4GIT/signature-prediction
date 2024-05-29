% Calculate signatures from Caravan dataset
close all
clear all
clc

%___________________________________________________________________________________
% Add TOSSH toolbox to the path
baseDir = 'C:\Users\flipl\dev';
TOSSHDir = 'TOSSH\TOSSH_code';
addpath(genpath(fullfile(baseDir, TOSSHDir)));

% Define directories and file type
data_dir = 'G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data';
caravan_dir = 'Caravan1.4';
attributes_dir = 'attributes';
timeseries_dir = 'timeseries';
data_type = 'csv';
caravan_data = 'hysets';
out_dir = 'G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures';

%___________________________________________________________________________________
% Read metadata
attrs_geo = readtable(fullfile(data_dir, caravan_dir, attributes_dir, caravan_data, ['attributes_other_hysets.' data_type]));
attrs_geo_names = attrs_geo.Properties.VariableNames;
% disp(head(attrs_geo));

% Filter data for US gauges
us_gauges = attrs_geo(strcmp(attrs_geo.country, 'United States of America'), :);
% disp(head(us_gauges));

% Number of gauges
numGauges = height(us_gauges);

%___________________________________________________________________________________
% Prepare parallel pool
% Specify the number of workers
numWorkers = 16;  % Adjust based on your system capabilities

% Set up the parallel pool
pool = gcp('nocreate');
if isempty(pool)
    parpool(numWorkers);  % Start a parallel pool
end

if isempty(gcp('nocreate'))
    parpool;  % Start a parallel pool using default settings
end

% Initialize a Composite to store results from each worker
resultsComp = Composite();

% Progress update setup
disp('Starting processing...');
totalIterations = numGauges;
progressStepSize = 100; % How often to update progress percentage

%___________________________________________________________________________________
% Loop through each gauge in us_gauges and collect data
parfor idx = 1:numGauges
    % Get the gauge id
    us_gauge = us_gauges(idx, :);
    gauge_id = cell2mat(us_gauge.gauge_id);
    fprintf("Currently processing %s\n", gauge_id)

    %___________________________________________________________________________________
    % Data preparation
    % Load data and convert it to datetime table 
    file_path = fullfile(data_dir, caravan_dir, timeseries_dir,data_type, caravan_data, [char(us_gauge.gauge_id) '.' data_type]);
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
    plot_results = false;

    %___________________________________________________________________________________
    % Signature calculation
    signatures = calc_All(...
       Q, t, P, PET, T);
    % Make table with IDs
    signatures.gauge_id = gauge_id;
    signatures = struct2table(signatures);
    
    % Store the results in the Composite variable
    resultsComp{idx} = signatures;

    % Update the progress display
    if mod(idx, progressStepSize) == 0
        fprintf('Progress: %d%% completed\n', floor((idx/totalIterations) * 100));
    end
end

% Collect results from all workers
results = table();
for idx = 1:numGauges
    if ~isempty(resultsComp{idx})
        results = [results; resultsComp{idx}];
    end
end

% Save the table to a CSV file
% remove FDC to save space
results.FDC = [];
results.FDC_error_str = [];
writetable(results, fullfile(out_dir, 'out.csv'), 'WriteVariableNames', true);
fprintf('Finished the analysis. Results are saved to %s\n', fullfile(out_dir, 'out.csv'));


