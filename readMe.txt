#########################################
Credentials
#########################################

# Login:
# ssh pi@raspberryPi
# password: What's better than a Rapsberry?.lower()

#########################################
Wiring
#########################################

# Raspberry wire description:
# Description           Pi Pin      Breakoutboard           High-Voltage Board
# VDD MCP3201 (5V)      4           Breakoutboard: 8        NC
# SPI CLK               23          Breakoutboard: 7        NC
# MCP3201 MISO          21          Breakoutboard: 6        NC
# /CS (CE0_N)           24          Breakoutboard: 5        NC
# VSS MCP3201 (GND)     9           Breakoutboard: 4        NC
# IN- MCP3201 (GND)     39          Breakoutboard: 3        NC
# IN+ MCP3201           NC          Breakoutboard: 2        TMCS1100 VOut (Pin7)
# VRef MCP3201 (5V)     4           Breakoutboard: 1        NC
# VS TMCS1100 (5V)      2           NC                      Pin 8
# GND TMCS1100 (GND)    6           NC                      Pin 5   

#########################################
Required Libraries
#########################################

    - Python (apt install / apt-get install / pip)
        - spidev            sudo apt install python3-spidev (Not required anymore due to sampling with C)
        - pandas            sudo apt install python3-pandas
        - numpy             sudo apt install python3-numpy
        - pip               sudo apt install python3-pip
        - dash              pip3 install dash --break-system-packages
        - plotly.express    pip3 install plotly --break-system-packages
    - C
        - Cython            sudo apt install cython3
        - bcm2835           sudo apt-get install bcm2835
        - python3-dev       sudo apt install python3-dev
        - gcc               sudo apt install gcc

#########################################
Raspberry Pi autostart behaviour
#########################################

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

Stop/Start systemctl Services:
    sudo systemctl stop power_monitor.service
    sudo systemctl stop dashboard.service

    sudo systemctl start power_monitor.service
    sudo systemctl start dashboard.service

#########################################
Compiling new C solution
#########################################

Compiling new C solution:
    Necessary files:
        setup.py
        spi_reader.pyx
        spi_backend.c
        spi_backend.h
    Commands:
        find . -name "*.c" -delete
        find . -name "*.so" -delete
        rm -rf build
        python3 setup.py build_ext --inplace


#########################################
Network Managment (WiFi)
#########################################

Check currently defined known networks:
    - nmcli connection show
Add a new network:
    - nmcli connection add type wifi ssid "SSID OF THE NETWORK" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "PASSWORD OF THE NETWORK" connection.id "NAME"
Manually connect to a existing network:
    - nmcli connection up "NAME"
Set connection priorities to network:
    - nmcli connection modify "NAME" connection.autoconnect-priority 10
    - nmcli connection modify "NAME" connection.autoconnect-priority 5
Network connection history:
    - sudo journalctl -u NetworkManager -f


