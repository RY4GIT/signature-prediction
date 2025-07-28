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
hourly_dir = 'CAMELShourly';
caravan_dir = 'Caravan1.5';
attributes_dir = 'attributes';
timeseries_dir = 'timeseries';
data_type = 'csv';

currentDate = datestr(now, 'yyyymmdd');
out_dir = fullfile(cloud_dir, 'out', 'signatures', ['test_hourlyCAMELS_', currentDate]);
out_filename = 'out_sigEvent.csv';
if ~exist(out_dir, 'dir')
    mkdir(out_dir);  % This will create the directory and any necessary subdirectories
    fprintf('Directory created: %s\n', out_dir);
else
    fprintf('Directory already exists: %s\n', out_dir);
end

%___________________________________________________________________________________
% Read metadata
attrs_geo = readtable(fullfile(data_dir, caravan_dir, attributes_dir, "camels", "attributes_other_camels.csv"));
attrs_geo_names = attrs_geo.Properties.VariableNames;
% disp(head(attrs_geo));

% Filter data for US gauges
us_gauges = attrs_geo(strcmp(attrs_geo.country, 'United States of America'), :);
% disp(head(us_gauges));

% Number of gauges
numGauges = height(us_gauges);

% Parameter config
config_OF = readtable('config_overlandflow.csv');
config_recession = readtable('config_recession.csv');
plot_results = false;

% Initialize
resultsCell = cell(numGauges, 1);


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
parfor idx = 1:numGauges
    try
        % Get the gauge id
        gauge_id = cell2mat(us_gauges(idx, :).gauge_id);
        fprintf("Currently processing %s\n", gauge_id)

        % Get the gauge number
        gauge_num = extractAfter(gauge_id, '_');
        fprintf("Gauge number: %s\n", gauge_num)



        %___________________________________________________________________________________
        % Data preparation

        % Load data and convert it to datetime table
        try
            q_file_path = fullfile(data_dir, hourly_dir, "usgs_streamflow", [gauge_num '-usgs-hourly.' data_type]);
            q_data = readtable(q_file_path);
        catch
            fprintf("No USGS data found for %s\n", gauge_id)
            continue
        end

        % Streamflow data
        q_data.date = datetime(q_data.date, 'InputFormat', 'yyyy-MM-dd');
        q_tt = table2timetable(q_data, 'RowTimes', 'date');
        %     disp(head(data_timetable));
        % plot(q_tt.QObs_mm_h_)

        % NLDAS forcing
        nldas_file_path = fullfile(data_dir, hourly_dir, "nldas_hourly", [gauge_num '_hourly_nldas.' data_type]);
        nldas_data = readtable(nldas_file_path);
        nldas_data.date = datetime(nldas_data.date, 'InputFormat', 'yyyy-MM-dd');
        nldas_tt = table2timetable(nldas_data, 'RowTimes', 'date');

        % Synchronize the timetables using NLDAS as temporal baseline
        data = synchronize(q_tt, nldas_tt, 'union', 'fillwithmissing');

        % Prepare TOSSH imput
        Q = num2cell(data.QObs_mm_h_,1); %mm/day
        t = num2cell(data.date,1);
        P = num2cell(data.total_precipitation,1);
        PET = num2cell(data.potential_evaporation,1);
        T = num2cell(data.temperature,1);

        %___________________________________________________________________________________
        % Get parameters

        % Overland flow
        ws_code = str2double(gauge_num(1:2));
        OF_param = config_OF(config_OF.ws_code == ws_code, :);


        %___________________________________________________________________________________
        % Event separation & IE SE signatures
        IE_effect = NaN(size(Q,1),1);
        SE_effect = NaN(size(Q,1),1);
        IE_thresh_signif = NaN(size(Q,1),1);
        IE_thresh = NaN(size(Q,1),1);
        SE_thresh_signif = NaN(size(Q,1),1);
        SE_thresh = NaN(size(Q,1),1);
        SE_slope = NaN(size(Q,1),1);
        Storage_thresh_signif = NaN(size(Q,1),1);
        Storage_thresh = NaN(size(Q,1),1);
        min_Qf_perc = NaN(size(Q,1),1);
        R_Pvol_RC = NaN(size(Q,1),1);
        R_Pint_RC = NaN(size(Q,1),1);
        OF_error_str = strings(size(Q,1),1);

        [IE_effect,SE_effect,IE_thresh_signif,IE_thresh, ...
            SE_thresh_signif,SE_thresh,SE_slope,Storage_thresh, ...
            Storage_thresh_signif,min_Qf_perc,R_Pvol_RC, R_Pint_RC,~,OF_error_str] ...
            = sig_EventGraphThresholds(Q{1},t{1},P{1},...
            'min_termination', OF_param.min_termination, ...
            'min_duration', OF_param.min_duration, ...
            'min_intensity_day', OF_param.min_intensity_day, ...
            'min_intensity_day_during', OF_param.min_intensity_day_during, ...
            'max_recessiondays', OF_param.max_recessiondays, ...
            'plot_results',plot_results);

        results = [];
        results.gauge_id = gauge_id;
        results.IE_effect = IE_effect;
        results.SE_effect = SE_effect;
        results.IE_thresh_signif = IE_thresh_signif;
        results.SE_thresh_signif = SE_thresh_signif;
        results.IE_thresh = IE_thresh;
        results.SE_thresh = SE_thresh;
        results.SE_slope = SE_slope;
        results.Storage_thresh_signif = Storage_thresh_signif;
        results.Storage_thresh = Storage_thresh;
        results.min_Qf_perc = min_Qf_perc;
        results.R_Pvol_RC = R_Pvol_RC;
        results.R_Pint_RC = R_Pint_RC;
        results.OF_error_str = OF_error_str;

        % Make table
        signatures = struct2table(results);
%         signatures.gauge_id = gauge_id; % this somehow doesn't work when
%         doing vertcat
        
        % Store the results in the Composite variable
        resultsCell{idx} = signatures;

    catch ME
        fprintf('Error at index %d: %s\n', idx, ME.message);

        % Create an empty output
        fieldNames = {
            'IE_effect', 'SE_effect', ...
            'IE_thresh_signif', 'SE_thresh_signif', 'IE_thresh', 'SE_thresh', 'SE_slope', ...
            'Storage_thresh_signif', 'Storage_thresh', 'min_Qf_perc', 'R_Pvol_RC', 'R_Pint_RC', 'OF_error_str'
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
        resultsCell{idx} = signatures;

    end
end

% Combine all results into one table after the loop
results = vertcat(resultsCell{:});

% Save the table to a CSV file
writetable(results, fullfile(out_dir, out_filename), 'WriteVariableNames', true);
fprintf('Finished the analysis. Results are saved to %s\n', fullfile(out_dir, out_filename));
fprintf('Total processing time: %.2f seconds\n', toc(totalTimer));

diary off;