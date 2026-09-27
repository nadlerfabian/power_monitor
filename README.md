# Raspberry Pi Power Monitor

This project implements a Raspberry Pi based power monitoring system.

The Raspberry Pi reads current measurements through an MCP3201 ADC and a
TMCS1100 current sensor. The collected measurements are processed and displayed
in a Dash dashboard.

The application consists of two main services:

- Power monitoring and data acquisition
- Web-based monitoring dashboard

#########################################
Remote Access
#########################################

# SSH login:
# ssh pi@raspberryPi
#
# Credentials are configured locally and are not stored in this repository.

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
Requirements
#########################################

Hardware:
    - Raspberry Pi
    - MCP3201 ADC
    - TMCS1100 current sensor
    - Breakout board

Software:
    - Raspberry Pi OS
    - Python 3
    - GCC
    - Cython


#########################################
Project Structure
#########################################

Main components:

    setup.py        Cython build configuration
    spi_reader.pyx  Python interface for the SPI backend
    spi_backend.c   Low-level SPI implementation
    spi_backend.h   SPI backend declarations

#########################################
Installation
#########################################

Install system dependencies:

    sudo apt update
    sudo apt install python3-pandas python3-numpy python3-pip
    sudo apt install cython3 bcm2835 python3-dev gcc

Install Python dependencies:

    pip3 install dash --break-system-packages
    pip3 install plotly --break-system-packages

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
Usage
#########################################

Check whether the services are running:

    sudo systemctl status power_monitor.service
    sudo systemctl status dashboard.service

Start the services manually:

    sudo systemctl start power_monitor.service
    sudo systemctl start dashboard.service

Stop the services:

    sudo systemctl stop power_monitor.service
    sudo systemctl stop dashboard.service

View service logs:

    sudo journalctl -u power_monitor.service
    sudo journalctl -u dashboard.service

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


