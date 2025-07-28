
folder_nldas = "E:\CAMELS_hourly\nldas_hourly_csv.tar\nldas_hourly";
folder_reduced = "E:\CAMELS_hourly\nldas_rain_hourly";

listing = dir(folder_nldas);

for i = 3:length(listing)
    %Create reduced table with only date and rainfall
    filename = listing(i).name;

    ffile = fullfile(folder_nldas,filename);

    ftable = readtable(ffile);

    ftable_reduced = ftable(:,["date","total_precipitation"]);

    ffile_new = fullfile(folder_reduced,filename);

    writetable(ftable_reduced,ffile_new);

    %Process data to get maximum hourly and daily total rain for each day
    tt_reduced = table2timetable(ftable_reduced);

    tt_reduced_dailysum = retime(tt_reduced,"daily","sum");
    tt_reduced_dailysum = renamevars(tt_reduced_dailysum,"total_precipitation","daily_precipitation");

    tt_reduced_dailymax = retime(tt_reduced,"daily","max");
    tt_reduced_dailymax = renamevars(tt_reduced_dailymax,"total_precipitation","max_hourly_precipitation");

    tt_dailysummax = [tt_reduced_dailymax,tt_reduced_dailysum];

    tt_dailysummax.max_hourly_frac = tt_dailysummax.max_hourly_precipitation ./ tt_dailysummax.daily_precipitation;
    tt_dailysummax.max_hourly_frac(tt_dailysummax.daily_precipitation==0)=0;

    tt_max_hourly_frac = tt_dailysummax(:,"max_hourly_frac");

    [ffile_new_pathstr, ffile_new_name, ffile_new_ext] = fileparts(ffile_new);
    ffile_new_mat = fullfile(folder_reduced,strcat(ffile_new_name,'.mat'));
    save(ffile_new_mat,"tt_max_hourly_frac")


end



    



