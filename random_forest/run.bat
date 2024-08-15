@echo off

set project_dir=C:\Users\flipl\dev\signature-prediction\random_forest
set config_dir=%project_dir%\configs

for %%i in (11 1210 6713 81 82 91 92) do (
    echo Running experiment with %config_dir%\config_ecoregion_%%i.yml
    Rscript main_mp.R %config_dir%\config_ecoregion_%%i.yml
    echo Experiment with %config_dir%\config_ecoregion_%%i.yml finished
)

echo Running experiment with %config_dir%\config_caravan_us.yml
Rscript main_mp.R %config_dir%\config_caravan_us.yml
echo Experiment with %config_dir%\config_caravan_us.yml finished

pause
