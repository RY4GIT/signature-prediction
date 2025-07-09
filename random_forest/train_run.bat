@echo off

set project_dir=C:\Users\flipl\dev\signature-prediction\random_forest
set config_dir=%project_dir%\configs\win

REM for %%i in (11 1210 6713 81 82 91 92) do (
REM     echo Running experiment with %config_dir%\config_ecoregion_%%i.yml
REM     Rscript main_mp.R %config_dir%\config_ecoregion_%%i.yml
REM     echo Experiment with %config_dir%\config_ecoregion_%%i.yml finished
REM )

@REM echo Running experiment with %config_dir%\config_test.yml
@REM Rscript train_main_mp.R %config_dir%\config_test.yml
@REM echo Experiment with %config_dir%\config_test.yml finished

@REM echo Running experiment with %config_dir%\config_20250517_baseline.yml
@REM Rscript train_main_mp.R %config_dir%\config_20250517_baseline.yml
@REM echo Experiment with %config_dir%\config_20250517_baseline.yml finished

@REM echo Running experiment with %config_dir%\config_20250517_camels.yml
@REM Rscript train_main_mp.R %config_dir%\config_20250517_camels.yml
@REM echo Experiment with %config_dir%\config_20250517_camels.yml finished

@REM echo Running experiment with %config_dir%\config_20250517_gages2_attrs.yml
@REM Rscript train_main_mp.R %config_dir%\config_20250517_gages2_attrs.yml
@REM echo Experiment with %config_dir%\config_20250517_gages2_attrs.yml finished

@REM echo Running experiment with %config_dir%\config_20250517_gages2_ref.yml
@REM Rscript train_main_mp.R %config_dir%\config_20250517_gages2_ref.yml
@REM echo Experiment with %config_dir%\config_20250517_gages2_ref.yml finished

@REM echo Running experiment with %config_dir%\config_20250517_gages2.yml
@REM Rscript train_main_mp.R %config_dir%\config_20250517_gages2.yml
@REM echo Experiment with %config_dir%\config_20250517_gages2.yml finished

echo Running experiment with %config_dir%\config_test_SHAP.yml
Rscript train_main_mp.R %config_dir%\config_test_SHAP.yml
echo Experiment with %config_dir%\config_test_SHAP.yml finished

pause
