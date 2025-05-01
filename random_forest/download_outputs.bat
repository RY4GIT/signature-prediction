@echo off
REM Configuration
SET remoteUser=raraki
SET remoteServer=forge.eri.ucsb.edu
SET remotePath=/home/raraki/data/signature-prediction/out/rf
SET localPath=C:/Users/flipl/Downloads

SET date=20250430

REM  1) SCP all the cluster ZIPs at once
scp %remoteUser%@%remoteServer%:"%remotePath%/output_raraki_%date%_cluster_*.zip" %localPath%

REM  2) Unzip each one in turn
FOR %%F IN ("%localPath%\*.zip") DO (
    echo Extracting %%~nF.zip…
    powershell -NoProfile -Command ^ "Expand-Archive -LiteralPath '%%~fF' -DestinationPath '%localPath%' -Force"
)

echo All files copied to %localPath%