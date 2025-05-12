@echo off

set project_dir=C:\Users\flipl\dev\signature-prediction\random_forest
set config_dir=%project_dir%\configs

REM for %%i in (11 1210 6713 81 82 91 92) do (
REM     echo Running experiment with %config_dir%\config_ecoregion_%%i.yml
REM     Rscript main_mp.R %config_dir%\config_ecoregion_%%i.yml
REM     echo Experiment with %config_dir%\config_ecoregion_%%i.yml finished
REM )

echo Running experiment with %config_dir%\config_test.yml
Rscript train_main_mp.R %config_dir%\config_test.yml
echo Experiment with %config_dir%\config_test.yml finished

pause
