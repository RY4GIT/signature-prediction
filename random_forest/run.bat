@echo off

set project_dir=C:\Users\flipl\dev\signature-prediction\random_forest

echo Running experiment with configs\config_test.yml
Rscript main_serial.R configs\config_test.yml
echo Experiment with configs\config_test.yml finished

pause