# Raspberry Pi Power Monitor

This project implements a Raspberry Pi-based power monitoring system.

The Raspberry Pi reads current measurements through an **MCP3201 ADC** and a **TMCS1100 current sensor**. The collected measurements are processed and displayed in a **Dash dashboard**.

The application consists of two main services:

* Power monitoring and data acquisition
* Web-based monitoring dashboard

## Remote Access

Connect to the Raspberry Pi via SSH:

```bash
ssh pi@raspberryPi
```

Credentials are configured locally and are not stored in this repository.

## Wiring

| Description        | Pi Pin | Breakout Board | High-Voltage Board    |
| ------------------ | -----: | -------------- | --------------------- |
| VDD MCP3201 (5V)   |      4 | Pin 8          | NC                    |
| SPI CLK            |     23 | Pin 7          | NC                    |
| MCP3201 MISO       |     21 | Pin 6          | NC                    |
| /CS (CE0_N)        |     24 | Pin 5          | NC                    |
| VSS MCP3201 (GND)  |      9 | Pin 4          | NC                    |
| IN- MCP3201 (GND)  |     39 | Pin 3          | NC                    |
| IN+ MCP3201        |     NC | Pin 2          | TMCS1100 VOut (Pin 7) |
| VRef MCP3201 (5V)  |      4 | Pin 1          | NC                    |
| VS TMCS1100 (5V)   |      2 | NC             | Pin 8                 |
| GND TMCS1100 (GND) |      6 | NC             | Pin 5                 |

## Requirements

### Hardware

* Raspberry Pi
* MCP3201 ADC
* TMCS1100 current sensor
* Breakout board

### Software

* Raspberry Pi OS
* Python 3
* GCC
* Cython

## Project Structure

The main components of the project are:

```text
setup.py         Cython build configuration
spi_reader.pyx   Python interface for the SPI backend
spi_backend.c    Low-level SPI implementation
spi_backend.h    SPI backend declarations
```

## Installation

Update the package index:

```bash
sudo apt update
```

Install the required system and Python packages:

```bash
sudo apt install python3-pandas python3-numpy python3-pip
sudo apt install cython3 bcm2835 python3-dev gcc
```

Install the required Python packages:

```bash
pip3 install dash --break-system-packages
pip3 install plotly --break-system-packages
```

### Dependencies

| Dependency  | Installation                                  | Purpose / Notes              |
| ----------- | --------------------------------------------- | ---------------------------- |
| pandas      | `sudo apt install python3-pandas`             | Data processing              |
| numpy       | `sudo apt install python3-numpy`              | Numerical operations         |
| pip         | `sudo apt install python3-pip`                | Python package manager       |
| Dash        | `pip3 install dash --break-system-packages`   | Web dashboard                |
| Plotly      | `pip3 install plotly --break-system-packages` | Data visualization           |
| Cython      | `sudo apt install cython3`                    | Python/C integration         |
| bcm2835     | `sudo apt install bcm2835`                    | Raspberry Pi hardware access |
| python3-dev | `sudo apt install python3-dev`                | Python development headers   |
| gcc         | `sudo apt install gcc`                        | C compiler                   |

> `spidev` is no longer required because SPI sampling is implemented in C.

## Usage

### Check Service Status

```bash
sudo systemctl status power_monitor.service
sudo systemctl status dashboard.service
```

### Start Services

```bash
sudo systemctl start power_monitor.service
sudo systemctl start dashboard.service
```

### Stop Services

```bash
sudo systemctl stop power_monitor.service
sudo systemctl stop dashboard.service
```

### View Service Logs

```bash
sudo journalctl -u power_monitor.service
sudo journalctl -u dashboard.service
```

## Autostart Configuration

Edit the systemd service definitions:

```bash
sudo nano /etc/systemd/system/power_monitor.service
sudo nano /etc/systemd/system/dashboard.service
```

Reload systemd after making changes:

```bash
sudo systemctl daemon-reload
```

Enable both services to start automatically:

```bash
sudo systemctl enable power_monitor.service
sudo systemctl enable dashboard.service
```

## Compiling the C Extension

The following files are required:

* `setup.py`
* `spi_reader.pyx`
* `spi_backend.c`
* `spi_backend.h`

Remove previous build artifacts:

```bash
find . -name "*.c" -delete
find . -name "*.so" -delete
rm -rf build
```

Compile the extension:

```bash
python3 setup.py build_ext --inplace
```

## Network Management

### Show Configured Networks

```bash
nmcli connection show
```

### Add a Wi-Fi Network

```bash
nmcli connection add type wifi ssid "SSID" \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "PASSWORD" \
    connection.id "NAME"
```

### Connect to an Existing Network

```bash
nmcli connection up "NAME"
```

### Set Network Priorities

```bash
nmcli connection modify "NAME" connection.autoconnect-priority 10
nmcli connection modify "NAME" connection.autoconnect-priority 5
```

A connection with a higher priority value is preferred.

### View NetworkManager Logs

```bash
sudo journalctl -u NetworkManager -f
```
