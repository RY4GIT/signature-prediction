
folder_nldas = "D:\data\CAMELShourly\nldas_hourly";
out_dir = "D:\data\CAMELShourly\nldas_max_hourly_fracP";

% Create output directory if it doesn't exist
if ~exist(out_dir, 'dir')
    mkdir(out_dir);
end

listing = dir(fullfile(folder_nldas, '*.csv'));
fprintf('Found %d CSV files to process\n', length(listing));

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
fprintf("Starting processing hourly CAMELS dataset\n");

% Define parsave function for parallel-safe saving

parfor i = 1:length(listing)
    % Create local copies of variables to ensure transparency
    local_folder_nldas = folder_nldas;
    local_out_dir = out_dir;
    
    fprintf("Currently processing [%d / %d]\n", i, length(listing))

    %Create reduced table with only date and rainfall
    filename = listing(i).name;

    ffile = fullfile(local_folder_nldas, filename);

    ftable = readtable(ffile);

    ftable_reduced = ftable(:,["date","total_precipitation"]);


    %Process data to get maximum hourly and daily total rain for each day
    tt_reduced = table2timetable(ftable_reduced, 'RowTimes', 'date');

    tt_reduced_dailysum = retime(tt_reduced,"daily","sum");
    tt_reduced_dailysum = renamevars(tt_reduced_dailysum,"total_precipitation","daily_precipitation");

    tt_reduced_dailymax = retime(tt_reduced,"daily","max");
    tt_reduced_dailymax = renamevars(tt_reduced_dailymax,"total_precipitation","max_hourly_precipitation");

    tt_dailysummax = [tt_reduced_dailymax,tt_reduced_dailysum];

    tt_dailysummax.max_hourly_frac = tt_dailysummax.max_hourly_precipitation ./ tt_dailysummax.daily_precipitation;
    tt_dailysummax.max_hourly_frac(tt_dailysummax.daily_precipitation==0)=0;

    tt_max_hourly_frac = tt_dailysummax(:,"max_hourly_frac");

    [~, ffile_new_name, ~] = fileparts(filename);
    ffile_new_mat = fullfile(local_out_dir, strcat(ffile_new_name,'.mat'));
    
    % Use parsave function for parallel-safe saving
    parsave(ffile_new_mat, tt_max_hourly_frac);

end

% Parallel-safe save function
function parsave(fname, tt_max_hourly_frac)
    save(fname, 'tt_max_hourly_frac');
end

