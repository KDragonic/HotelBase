@echo off
cd /d C:\\Users\\WeB Voin\\Desktop\\HotelBase\\r_logs
for %%i in (*.log) do start cmd /c py "C:\\Users\\WeB Voin\\Desktop\\HotelBase\\print_log.py" "%%i"
