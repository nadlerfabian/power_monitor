import sys
sys.path.append('./cython')  # Adjust this path to point to the subdirectory
import spidev
import time
import math
import csv
from datetime import datetime
import gc
import os
import psutil
import numpy as np
import pandas as pd
import spi_reader

# Initialize SPI
# spi = spidev.SpiDev()
# spi.open(0, 0)  # Bus 0, Device 0 (but using custom /CS pin)
# spi.max_speed_hz = 2000000  # 2 MHz, MCP3201 supports up to 2 MHz
# spi.mode = 0b00  # SPI Mode 0 (CPOL=0, CPHA=0)
spi_reader.initialize_spi()

# CSV file setup
csv_file = "../data/power_usage.csv"
csv_header = ["DateTime", "Peak_Current(A)", "RMS_Current(A)", "Power(kW)"]

# For Logging purpose
# Initialize the DataFrame with 500 rows and the specified columns
max_logging_entries = 500
logging_data = {
    "PosSamples": [0] * max_logging_entries,
    "TotalSamples": [0] * max_logging_entries
}
logging_df = pd.DataFrame(logging_data)

# Circular index counter
current_logging_index = 0
logging_rows_written = 0  # Track how many rows have been written

# Update the DataFrame
def update_dataframe(df, pos_samples, total_samples, current_index, rows_written):
    """
    Update the DataFrame at the current circular index with new values.
    """
    # Write data into the current index
    df.at[current_index, "PosSamples"] = pos_samples
    df.at[current_index, "TotalSamples"] = total_samples
    
    # Update the circular index
    current_index = (current_index + 1) % max_logging_entries
    rows_written = min(rows_written + 1, max_logging_entries)  # Increment written rows, cap at max_entries

    return current_index, rows_written

# Create or append to the CSV file
with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    file.seek(0, 2)  # Move to the end of the file
    if file.tell() == 0:  # If file is empty, write the header
        writer.writerow(csv_header)

# Function to read data from MCP3201
# def read_mcp3201():
#     raw_data = spi.xfer2([0x00, 0x00])  # MCP3201 expects 16 clock cycles
#     adc_value = ((raw_data[0] & 0x1F) << 7) | (raw_data[1] >> 1)  # Combine 12-bit ADC value
#     return adc_value

# Function to read waveform
def read_waveform(max_samples=5000, sample_duration=40):
    """Read waveform samples for a specified duration."""
    # samples = []
    # start_time = time.time()

    # while time.time() - start_time < sample_duration:
    #     adc_value = read_mcp3201()
    #     samples.append(adc_value)
    print(time.time())
    samples = spi_reader.collect_samples(5000, sample_duration) # Max buffer size: 2000, Duration: 40ms
    print(time.time())
    print(f"Taken Samples Amount: {len(samples)}, Samples taken: {samples}")
    return samples

# Function to extract positive half-cycle
def extract_positive_half_cycle(samples, min_samples=30, baseline=5, outlierTolerance=3):
    """Extract a clean positive half-cycle from the waveform."""
    zeroCrossFlag = False
    start_idx = None
    end_idx = None

    for i in range(1, len(samples) - 1):
        # Detect the first rising edge (start of the half-cycle)
        if(start_idx is None and len(samples) > i + outlierTolerance and not zeroCrossFlag and all(samples[i + k] < baseline for k in range(outlierTolerance + 1))):
            if(samples[i] < baseline):
                zeroCrossFlag = True
        if(zeroCrossFlag):
            if(start_idx is None and samples[i] > baseline):
                start_idx = i
            elif(start_idx and len(samples) > i + outlierTolerance and all(samples[i + k] < baseline for k in range(outlierTolerance + 1))):   # Checks if we really reached the bottom, this helps at dealing with faulty values for example: [58, 44, 60, 79, 1, 97, 81, 47, 47], here sample loop wont break due to the 1 value
                end_idx = i
                if(end_idx-start_idx < min_samples):
                    start_idx = end_idx+outlierTolerance + 1
                    end_idx = None
                else:
                    break
    # If no valid cycle is detected, return an empty list
    if not end_idx:
        print("No valid positive half-cycle detected.")
        return []
    return samples[start_idx:end_idx]



# Function to calculate peak and RMS current
def calculate_peak_and_rms(samples):
    if len(samples) == 0:
        return 0, 0  # No samples collected

    print(f"Positive Sample Amount: {len(samples)} / Positive Samples: {samples}")


    # Convert samples to voltage
    samples_voltage = [(sample / 4095.0) * 5.1 for sample in samples]

    # Convert voltage to current using sensor sensitivity
    sensitivity = 0.4  # Example: 0.4 V/A for TMCS1100A4
    samples_current = [voltage / sensitivity for voltage in samples_voltage]

    # Calculate RMS value
    rms_value = np.sqrt(np.mean(np.square(samples_current)))

    # Peak value (max of the samples)
    peak_voltage = max(samples_voltage)
    peak_current = peak_voltage / sensitivity

    return peak_current, rms_value

try:
    while True:
        gc.disable()
        # Read waveform for a longer duration
        samples = read_waveform(max_samples=5000, sample_duration=40)
        # Extract positive half-cycle
        positive_samples = extract_positive_half_cycle(samples, baseline=5)

        current_logging_index, logging_rows_written = update_dataframe(logging_df, len(positive_samples), len(samples), current_logging_index, logging_rows_written)

        # If positive samples are found, calculate metrics
        if positive_samples is not None:
            # Calculate peak and RMS current
            peak_current, rms_current = calculate_peak_and_rms(positive_samples)

            # Calculate power
            power_used = rms_current * 230 / 1000  # Power in kW

            # Get current time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Log to CSV
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([current_time, round(peak_current, 6), round(rms_current, 6), round(power_used, 6)])

            # Print the results
            print(f"Peak Current: {peak_current:.2f}A, RMS Current: {rms_current:.2f}A, Power Usage: {power_used:.2f}kW")
            temp_logging_df = logging_df.iloc[:logging_rows_written]
            print(f"Avg Total Samples: {temp_logging_df['TotalSamples'].mean():.2f} / Avg Positive Samples: {temp_logging_df['PosSamples'].mean():.2f} / Min Total Samples: {temp_logging_df['TotalSamples'].min()} / Min Positive Samples: {temp_logging_df['PosSamples'].min()} / Null Pos Values (Amount): {sum(temp_logging_df['PosSamples'] == 0)}")
        else:
            print("No valid positive half-cycle detected or insufficient samples.")

        gc.enable()
        time.sleep(10)  # Perform detection every 10 seconds

except KeyboardInterrupt:
    print("Exiting...")
finally:
    spi_reader.close_spi()
