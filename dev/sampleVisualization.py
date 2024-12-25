# import numpy as np
# import matplotlib.pyplot as plt

# # Example data
# data = [53, 40, 48, 68, 63, 58, 30, 60, 62, 53, 34, 52, 91, 91, 78, 89, 62, 68, 58, 
#         43, 68, 90, 45, 53, 43, 86, 42, 61, 69, 66, 74, 42, 67, 70, 69, 58, 77, 30, 
#         66, 77, 81, 67, 76, 95, 117, 88, 151, 140, 166, 137, 100, 179, 95, 102, 100, 
#         121, 97, 118, 119, 86, 98, 88, 84, 126, 129, 91, 79, 93, 125, 210, 352, 358, 
#         406, 389, 402, 430, 425, 381, 354, 378, 365, 334, 292, 262, 204, 53, 60, 44, 
#         40, 10, 10, 6, 31, 9]

# # Convert samples to voltage
# samples_voltage = [(sample / 4095.0) * 5.1 for sample in data]

# # Convert voltage to current using sensor sensitivity
# sensitivity = 0.4  # Example: 0.4 V/A for TMCS1100A4
# samples_current = [voltage / sensitivity for voltage in samples_voltage]
# # RMS calculation
# rms_value = np.sqrt(np.mean(np.square(samples_current)))

# # Plotting
# plt.figure(figsize=(12, 6))
# plt.plot(samples_current, label='Current Samples', marker='o', linestyle='-')
# plt.axhline(y=rms_value, color='r', linestyle='--', label=f'RMS Value = {rms_value:.2f}')
# plt.title('Visualization of RMS Calculation')
# plt.xlabel('Sample Index')
# plt.ylabel('Current (A)')
# plt.legend()
# plt.grid(True)
# plt.show()

# rms_value

import pandas as pd

# Initialize the DataFrame with 500 rows and the specified columns
max_entries = 500
data = {
    "PosSamples": [0] * max_entries,
    "TotalSamples": [0] * max_entries
}
df = pd.DataFrame(data)

# Circular index counter
current_index = 0

# Function to update the DataFrame
def update_dataframe(df, pos_samples, total_samples, current_index):
    """
    Update the DataFrame at the current circular index with new values.
    """
    # Write data into the current index
    df.at[current_index, "PosSamples"] = pos_samples
    df.at[current_index, "TotalSamples"] = total_samples
    
    # Update the circular index
    current_index = (current_index + 1) % max_entries
    return current_index

# Example usage
for cycle in range(550):  # Simulate 550 cycles
    pos_samples = cycle * 2  # Example value for PosSamples
    total_samples = cycle * 3  # Example value for TotalSamples
    current_index = update_dataframe(df, pos_samples, total_samples, current_index)

# Print the resulting DataFrame
print(df)
