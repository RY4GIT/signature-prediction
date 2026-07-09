% Calculate signatures from Caravan dataset
% Ryoko Araki (@ry4git), 2024
% Current directly should be ..\signature-prediction\signatures\.

% Cleaning
% close all
% clear all
% delete(gcp('nocreate'))
% clc

% Start the total runtime timer
totalTimer = tic;
diary('log.txt');

%___________________________________________________________________________________
% CHANGE HERE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Declare signature function/category to use
sig_cat = 'calc_All_custom';
% 'calc_All', 'calc_All_custom', 'calc_McMillan_OverlandFlow', 'calc_McMillan_Groundwater',
% 'calc_Addor', 'calc_Sawicz', 'calc_Euser',  'calc_BasicSet'

% Choose which Caravan gaguges to run: 'hysets' or 'camels'
caravan_data = 'camels';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%___________________________________________________________________________________
% Add TOSSH toolbox to the path
baseDir = 'Y:\Gruppen\cathyd\mcmillan\signatures_processes'; % 'G:\Araki\proj' on lab computer
TOSSHDir = 'TOSSH\TOSSH_code';
addpath(genpath(fullfile(baseDir, TOSSHDir)));

% Define directories and file type
cloud_dir = 'C:\Users\mcmillan\Documents\Results'; % 'G:\Araki' on lab computer
data_dir = 'C:\Users\mcmillan\Documents\CAMELS_DE';
caravan_dir = 'Caravan1.5';
attributes_dir = 'attributes';
timeseries_dir = 'timeseries';
timeseries_sim_dir = 'timeseries_simulated';
data_type = 'csv';

currentDate = datestr(now, 'yyyymmdd');
out_dir = fullfile(cloud_dir, 'out', 'signatures', ['caravan_', caravan_data, '_', currentDate]);
out_filename = ['out_' sig_cat '.csv'];
if ~exist(out_dir, 'dir')
    mkdir(out_dir);  % This will create the directory and any necessary subdirectories
    fprintf('Directory created: %s\n', out_dir);
else
    fprintf('Directory already exists: %s\n', out_dir);
end

%___________________________________________________________________________________
%Read Gauge IDs
attrs_climate = readtable(fullfile(data_dir, 'CAMELS_DE_climatic_attributes.csv'));
attrs_climate_names = attrs_climate.Properties.VariableNames;
disp(head(attrs_climate));

% Read metadata
%attrs_geo = readtable(fullfile(data_dir, caravan_dir, attributes_dir, caravan_data, ['attributes_other_' caravan_data '.' data_type]));
%attrs_geo_names = attrs_geo.Properties.VariableNames;
% disp(head(attrs_geo));

% Filter data for US gauges
%us_gauges = attrs_geo(strcmp(attrs_geo.country, 'United States of America'), :);
% disp(head(us_gauges));

% Number of gauges
numGauges = height(attrs_climate);

% Parameter config
config_OF = readtable('config_overlandflow_standard_DE.csv');
config_recession = readtable('config_recession.csv');

plot_results = true;

%___________________________________________________________________________________
% % Prepare parallel pool
% %
% % Specify the number of workers
% numWorkers = 6;  % Adjust based on your system capabilities
% 
% % Set up the parallel pool
% pool = gcp('nocreate');
% if isempty(pool)
%     parpool(numWorkers);  % Start a parallel pool
% end
% 
% % Initialize the cell array for results
% resultsCell = cell(numGauges, 1);
% 
% % Progress update setup
% fprintf("Starting processing ... %s dataset", caravan_data);

%___________________________________________________________________________________
% Loop through each gauge in us_gauges and collect data
for idx = 1:1 %numGauges
%parfor idx = 1:numGauges
    
    try
        % Get the gauge id
        gauge_id = cell2mat(attrs_climate(idx, :).gauge_id);
        fprintf("Currently processing %s\n", gauge_id)
        
        %___________________________________________________________________________________
        % Data preparation
        % Load data and convert it to datetime table
        file_path = fullfile(data_dir, timeseries_dir, ...
            ['CAMELS_DE_hydromet_timeseries_', gauge_id '.' data_type]);
        data = readtable(file_path);
        data.date = datetime(data.date, 'InputFormat', 'MM/dd/yyyy');
        data_timetable = table2timetable(data, 'RowTimes', 'date');
        %     disp(head(data_timetable));

        %Read separate file with PET
        file_path = fullfile(data_dir, timeseries_sim_dir, ...
            ['CAMELS_DE_discharge_sim_', gauge_id '.' data_type]);
        data_sim = readtable(file_path);
 
        % Prepare TOSSH imput
        Q = num2cell(data.discharge_spec_obs,1); %mm/day
        t = num2cell(data.date,1);
        P = num2cell(data.precipitation_mean,1);
        PET = num2cell(data_sim.pet_hargreaves,1);
        T = num2cell(data.temperature_mean,1);
        
        %___________________________________________________________________________________
        % Get parameters
        
        if strcmp(sig_cat,'calc_All_custom')
            
            try
                % Overland flow
                % parts = split(gauge_id, '_');
                % gauge_code = parts{2};
                % ws_code = str2double(gauge_code(1:2));
                %OF_param = config_OF(config_OF.ws_code == ws_code, :);
                OF_param = config_OF(1, :);
                
                
                % Recession
                p95 = prctile(data.discharge_spec_obs, 95);
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
            'Storage_thresh_signif', 'Storage_thresh', 'min_Qf_perc', 'R_Pvol_RC', 'R_Pint_RC', 'OF_error_str', ...
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
results.gauge_id = attrs_climate.gauge_id(1:numGauges);

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