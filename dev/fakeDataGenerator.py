import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_realistic_data(output_file, start_year=2020, end_year=2024, interval_minutes=15, monthly_target_kwh=100):
    # Generate timestamps at the specified interval
    date_rng = pd.date_range(start=datetime(start_year, 1, 1), 
                             end=datetime(end_year, 12, 31, 23, 59), 
                             freq=f'{interval_minutes}T')

    # Generate realistic power usage values
    def generate_power(hour):
        if 6 <= hour < 9:  # Morning peak
            return np.random.uniform(0.8, 1.5)  # kW
        elif 18 <= hour < 22:  # Evening peak
            return np.random.uniform(1.0, 1.8)  # kW
        elif 22 <= hour or hour < 6:  # Night low usage
            return np.random.uniform(0.1, 0.5)  # kW
        else:  # Daytime usage
            return np.random.uniform(0.3, 1.0)  # kW

    # Create power data based on time of day
    power_data = [generate_power(ts.hour) for ts in date_rng]

    # Calculate scaling factor
    total_hours = len(date_rng) / (60 / interval_minutes)
    total_kwh = sum(power_data) * (interval_minutes / 60)
    scaling_factor = monthly_target_kwh / (total_kwh / (total_hours / (24 * 30)))

    # Apply scaling factor to adjust power values
    scaled_power_data = [power * scaling_factor for power in power_data]

    # Calculate corresponding current using 230V
    current_data = [power * 1000 / 230 for power in scaled_power_data]  # Current in Amperes (P = IV)

    # Create DataFrame
    df = pd.DataFrame({
        'DateTime': date_rng,
        'Peak_Current(A)': current_data,
        'Power(kW)': scaled_power_data
    })

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Realistic data saved to {output_file}")

# Example usage
generate_realistic_data("power_usage.csv", start_year=2020, end_year=2024, interval_minutes=15)
