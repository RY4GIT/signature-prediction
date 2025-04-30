@echo off
setlocal enabledelayedexpansion

REM Set the base input/output paths
set "BASE_DIR=G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\rf"
set "ZIP_TOOL=C:\Program Files\7-Zip\7z.exe"

REM Loop over clusters 0 to 5 and 'all'
for %%C in (0 1 2 3 4 5 all) do (
    echo.
    echo === Processing cluster %%C ===

    REM Define paths
    set "ZIP_FILE=%BASE_DIR%\output_raraki_20250429_cluster_%%C.zip"
    set "EXTRACT_DIR=%BASE_DIR%\output_raraki_20250429_cluster_%%C"
    set "NESTED_DIR=%EXTRACT_DIR%\home\raraki\data\signature-prediction\out\rf\output_raraki_20250429_cluster_%%C"

    REM Delete existing extract folder if it exists
    if exist "!EXTRACT_DIR!" (
        echo Deleting previous folder: !EXTRACT_DIR!
        rmdir /s /q "!EXTRACT_DIR!"
    )

    REM Extract ZIP file
    echo Extracting: !ZIP_FILE!
    "%ZIP_TOOL%" x "!ZIP_FILE!" -o"!EXTRACT_DIR!" -y >nul

    REM Move files from deep nested folder to the root extract folder
    if exist "!NESTED_DIR1!" (
        echo Flattening from nested path 1...
        xcopy /e /y /i "!NESTED_DIR1!\*" "!EXTRACT_DIR!\" >nul
        rmdir /s /q "!EXTRACT_DIR!\home"
    ) else if exist "!NESTED_DIR2!" (
        echo Flattening from nested path 2...
        xcopy /e /y /i "!NESTED_DIR2!\*" "!EXTRACT_DIR!\" >nul
        rmdir /s /q "!NESTED_DIR2!"
    ) else (
        echo WARNING: Neither expected path found for cluster %%C
    )

    echo Done with cluster %%C.
)

echo.
echo === All clusters processed ===
pause
