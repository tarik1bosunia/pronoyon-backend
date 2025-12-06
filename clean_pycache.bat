@echo off
echo ----------------------------------------
echo   Cleaning all __pycache__ folders...
echo ----------------------------------------

for /d /r %cd% %%d in (__pycache__) do (
    if exist "%%d" (
        echo Deleting: %%d
        rd /s /q "%%d"
    )
)

echo ----------------------------------------
echo   Done! All __pycache__ removed.
echo ----------------------------------------
pause
