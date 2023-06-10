@echo off
cd /d "C:\\Users\\%USERNAME%\\Desktop\\HotelBase\\r_logs"
for %%i in (*.log) do start cmd /c py "C:\\Users\\%USERNAME%\\Desktop\\HotelBase\\print_log.py" "%%i"
