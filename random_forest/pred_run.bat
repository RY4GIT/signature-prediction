@echo off

set project_dir=C:\Users\flipl\dev\signature-prediction\random_forest
set config_dir=%project_dir%\configs\win

set config_files=config_pred_hys_gg2_baddata config_pred_hys_only

for %%f in (%config_files%) do (
    set config_name=%%f
    echo Running experiment with %config_dir%\%%f.yml
    Rscript pred_main_serial.R %config_dir%\%%f.yml
    echo Experiment with %%f finished
)

pause
