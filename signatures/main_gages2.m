% Calculate signatures from GAGES2 catchment, that are overlapping with
% Caravan (CAMELS + HYSETS) gauges. Q, PET, T are from Caravan (ERA-5),
% while the P is replaced with surface water input data from Hammond, 2024:
% https://www.sciencebase.gov/catalog/item/6494515fd34ef77fcb014eb0

% Ryoko Araki (@ry4git), 2025

% Cleaning
close all
clear all
delete(gcp('nocreate'))
clc

% Start the total runtime timer
totalTimer = tic;
diary('log.txt');

%___________________________________________________________________________________
% Put config here
% Declare signature function/category to use
sig_cat = 'calc_All_custom';
% Choose which Caravan gaguges to run: 'hysets' or 'camels'
caravan_data_cat = 'camels';

%___________________________________________________________________________________
% Add TOSSH toolbox to the path
baseDir = 'C:\Users\flipl\dev'; % 'G:\Araki\proj' on lab computer
TOSSHDir = 'TOSSH\TOSSH_code';
addpath(genpath(fullfile(baseDir, TOSSHDir)));

% Define directories and file type
home_dir = 'G:\Shared drives\Signatures -- large scale\baseflow\RAraki'; % 'G:\Araki' on lab computer
data_dir = fullfile(home_dir, 'data');
caravan_dir = 'Caravan1.4';
attributes_dir = 'attributes';
timeseries_dir = 'timeseries';
data_type = 'csv';

swi_dir = 'surface_water_input\preprocessed';

currentDate = datestr(now, 'yyyymmdd');
out_dir = fullfile(home_dir, 'out', 'signatures', ['gages2_', caravan_data_cat, '_', currentDate]);
out_filename = ['out_' sig_cat '.csv'];
if ~exist(out_dir, 'dir')
    mkdir(out_dir);  % This will create the directory and any necessary subdirectories
    fprintf('Directory created: %s\n', out_dir);
else
    fprintf('Directory already exists: %s\n', out_dir);
end

%___________________________________________________________________________________
% Read Caravan metadata
attrs_geo = readtable(fullfile(data_dir, caravan_dir, attributes_dir, caravan_data_cat, ['attributes_other_' caravan_data_cat '.' data_type]));
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

%___________________________________________________________________________________
% Get list of filenames from teh gages2 surface water input
swi_fileinfo = dir(fullfile(data_dir, swi_dir, '*'));
swi_files = {swi_fileinfo.name};


%___________________________________________________________________________________
% Prepare parallel pool

% Specify the number of workers
numWorkers = 6;  % Adjust based on your system capabilities

% Set up the parallel pool
pool = gcp('nocreate');
if isempty(pool)
    parpool(numWorkers);  % Start a parallel pool
end

% Initialize the cell array for results
resultsCell = cell(numGauges, 1);

% Progress update setup
fprintf("Starting processing ... %s dataset", caravan_data_cat);

%___________________________________________________________________________________
% Loop through each gauge in us_gauges and collect data
% for idx = 1:numGauges
parfor idx = 1:numGauges
    try
        % Get the gauge id
        gauge_id = cell2mat(us_gauges(idx, :).gauge_id);
        fprintf("Currently processing %s\n", gauge_id)
        gauge_num = extractAfter(gauge_id, '_');

        % __________________________________________________________________________________
        % Check if the gauge_id exist in the surface water input file list
        % (i.e., the target caravan gauge is in gages2 set) 
        
        % Find filenames that contain gauge_num
        matchingFile = string(swi_files(contains(swi_files, gauge_num)));

       % Skip to the next iteration of the for loop
        if isempty(matchingFile)
            error('No matching files found for gauge ID: %s', gauge_num);
        end

                
        %___________________________________________________________________________________
        % Data preparation

        % Load Caravan data and convert it to datetime table
        file_path = fullfile(data_dir, caravan_dir, timeseries_dir, data_type, caravan_data_cat, [gauge_id '.' data_type]);
        caravan_data = readtable(file_path);
        caravan_data.date = datetime(caravan_data.date, 'InputFormat', 'yyyy-MM-dd');
        caradata_timetable = table2timetable(caravan_data, 'RowTimes', 'date');
        %     disp(head(data_timetable));

        % Load surface water input data and convert it to datetime table
        file_path = fullfile(data_dir, swi_dir, matchingFile);
        swi_data = readtable(file_path);
        swi_data.date = datetime(swi_data.date, 'InputFormat', 'yyyy-MM-dd');
        swidata_timetable = table2timetable(swi_data, 'RowTimes', 'date');

        % Find common dates
        common_dates = intersect(caradata_timetable.date, swidata_timetable.date);

        % Extract only the common rows
        cara_common = caradata_timetable(ismember(caradata_timetable.date, common_dates), :);
        swi_common = swidata_timetable(ismember(swidata_timetable.date, common_dates), :);
        start_date = cara_common.date(1);
        end_date = cara_common.date(end);

        % Prepare TOSSH imput
        surface_water_input = swi_common.melt_mm + swi_common.mix_mm + swi_common.rain_mm;
        Q = num2cell(cara_common.streamflow,1); %mm/day
        t = num2cell(cara_common.date,1);
        P = num2cell(surface_water_input,1); % Use surface water input instead of precipitation to account for snow effects
        PET = num2cell(cara_common.potential_evaporation_sum,1);
        T = num2cell(cara_common.temperature_2m_mean,1);
        
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
                p95 = prctile(cara_common.streamflow, 95);
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

        % Create an empty output
        fieldNames = {
            'AC1', 'AC1_error_str', 'BaseflowRecessionK', 'BaseflowRecessionK_error_str', ...
            'BaseflowMagnitude', 'BaseflowMagnitude_error_str', 'BFI', 'BFI_error_str', ...
            'EventGraphThresholds', 'EventGraphThresholds_error_str', 'EventRR', 'EventRR_error_str', ...
            'FDC', 'FDC_error_str', 'FDC_slope', 'FDC_slope_error_str', ...
            'FlashinessIndex', 'FlashinessIndex_error_str', 'HFD_mean', 'HFD_mean_error_str', ...
            'HFI_mean', 'HFI_mean_error_str', 'MRC_SlopeChanges', 'MRC_SlopeChanges_error_str', ...
            'PeakDistribution', 'PeakDistribution_error_str', 'PQ_Curve', 'PQ_Curve_error_str', ...
            'Q_CoV', 'Q_CoV_error_str', 'Q_mean', 'Q_mean_error_str', 'Q_mean_monthly', ...
            'Q_mean_monthly_error_str', 'Q_7_day_max', 'Q_7_day_max_error_str', 'Q_7_day_min', ...
            'Q_7_day_min_error_str', 'Q_skew', 'Q_skew_error_str', 'Q_var', 'Q_var_error_str', ...
            'QP_elasticity', 'QP_elasticity_error_str', 'RecessionParameters_a', 'RecessionParameters_b', 'RecessionParameters_T0', 'RecessionParameters_error_str', ...
            'RecessionK_early', 'RecessionK_early_error_str', 'Spearmans_rho', 'Spearmans_rho_error_str', ...
            'ResponseTime', 'ResponseTime_error_str', 'RLD', 'RLD_error_str', 'RR_Seasonality', ...
            'RR_Seasonality_error_str', 'SeasonalTranslation', 'SeasonalTranslation_error_str', ...
            'Recession_a_Seasonality', 'Recession_a_Seasonality_error_str', 'SnowDayRatio', ...
            'SnowDayRatio_error_str', 'SnowStorage', 'SnowStorage_error_str', 'StorageFraction', ...
            'StorageFraction_error_str', 'StorageFromBaseflow', 'StorageFromBaseflow_error_str', ...
            'TotalRR', 'TotalRR_error_str', 'VariabilityIndex', 'VariabilityIndex_error_str', ...
            'Q95', 'Q95_error_str', 'high_Q_duration', 'high_Q_duration_error_str', ...
            'high_Q_frequency', 'high_Q_frequency_error_str', 'IE_effect', 'SE_effect', ...
            'IE_thresh_signif', 'SE_thresh_signif', 'IE_thresh', 'SE_thresh', 'SE_slope', ...
            'Storage_thresh_signif', 'Storage_thresh', 'min_Qf_perc', 'OF_error_str', ...
            'AverageStorage', 'MRC_num_segments', 'MRC_num_segments_error_str', ...
            'First_Recession_Slope', 'Mid_Recession_Slope', 'EventRR_TotalRR_ratio'
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
        
        % Make table
        signatures = struct2table(signatures);
        resultsCell{idx} = signatures;
        
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