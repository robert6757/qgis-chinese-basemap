@echo off
setlocal enabledelayedexpansion

set "MAIN_PYTHON=%~dp0../chinese_basemap.py"

set "UI_DIR=%~dp0../ui"
set "PYTHON_DIR=%~dp0../main"
set "OUTPUT_TS=%~dp0../i18n/ChineseBasemap_zh-Hans.ts"

:: find all ui files.
set "UI_FILES="
for /r "%UI_DIR%" %%i in (*.ui) do (
    set "UI_FILES=!UI_FILES! "%%i""
)

:: find all python files.
set "PYTHON_FILES="
for /r "%PYTHON_DIR%" %%i in (*.py) do (
    set "PYTHON_FILES=!PYTHON_FILES! "%%i""
)

echo UI Files: %UI_FILES%
echo Python Files: %PYTHON_FILES%

:: exec pylupdate5
pylupdate5 %MAIN_PYTHON% %PYTHON_FILES% %UI_FILES% -ts "%OUTPUT_TS%"

endlocal