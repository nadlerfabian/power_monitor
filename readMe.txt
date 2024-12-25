# Login:
# ssh pi@raspberryPi
# password: arduino

# Raspberry wire description:
# Description           Pi Pin      Breakoutboard           High-Voltage Board
# VDD MCP3201 (5V)      4           Breakoutboard: 8        NC
# SPI CLK               23          Breakoutboard: 7        NC
# MCP3201 DataOut       7           Breakoutboard: 6        NC
# /CS                   11          Breakoutboard: 5        NC
# VSS MCP3201 (GND)     9           Breakoutboard: 4        NC
# IN- MCP3201 (GND)     NC          NC                      NC
# IN+ MCP3201           NC          Breakoutboard: 2        TMCS1100 VOut (Pin7)
# VRef MCP3201 (5V)     4           Breakoutboard: 1        NC
# VS TMCS1100 (5V)      2           NC                      Pin 8
# GND TMCS1100 (GND)    6           NC                      Pin 5   



Check program Status:
    sudo systemctl status power_monitor.service
    sudo systemctl status dashboard.service
Check history:
    sudo journalctl -u power_monitor.service
    sudo journalctl -u dashboard.service

Edit Autostart behaviour:
    sudo nano /etc/systemd/system/power_monitor.service
    sudo nano /etc/systemd/system/dashboard.service

    sudo systemctl daemon-reload

    sudo systemctl enable power_monitor.service
    sudo systemctl enable dashboard.service

Start/Stop systemctl Services:
    sudo systemctl stop power_monitor.service
    sudo systemctl stop dashboard.service

    sudo systemctl start power_monitor.service
    sudo systemctl start dashboard.service
