import numpy as np
import pandas as pd

# Set a random seed for reproducibility
np.random.seed(42)

# Number of transactions to simulate
num_transactions = 10000

# Transaction amount in dollars using a lognormal distribution (heavy-tailed)
amount = np.random.lognormal(mean=np.log(50), sigma=0.75, size=num_transactions)
amount = np.maximum(amount, 1)  # Minimum transaction amount is $1

# IP distance in km: 90% low values, 10% high outliers
ip_distance_low = np.random.exponential(scale=10, size=int(0.9 * num_transactions))
ip_distance_high = np.random.uniform(50, 500, size=int(0.1 * num_transactions))
ip_distance = np.concatenate([ip_distance_low, ip_distance_high])
np.random.shuffle(ip_distance)

# Device type: 1 for mobile (60%), 2 for desktop (30%), 3 for tablet (10%)
device_type_id = np.random.choice([1, 2, 3], size=num_transactions, p=[0.6, 0.3, 0.1])

# Time of day (0-23 hours): mixture of peak (around 14) and off-peak (around 2) times
time_peak = np.random.normal(loc=14, scale=2, size=int(0.7 * num_transactions))
time_offpeak = np.random.normal(loc=2, scale=2, size=int(0.3 * num_transactions))
time_of_day = np.concatenate([time_peak, time_offpeak])
time_of_day = np.clip(time_of_day, 0, 23)

# Transaction frequency: simulated with a Poisson distribution
tx_frequency = np.random.poisson(lam=1.5, size=num_transactions)

# Merchant risk factor (0.0 to 1.0): most merchants are low risk (Beta distribution)
merchant_risk = np.random.beta(a=2, b=8, size=num_transactions)

# Account age in days: exponential distribution with minimum bound (10 days) and maximum (10 years)
account_age = np.random.exponential(scale=1000, size=num_transactions)
account_age = np.clip(account_age, 10, 3650)

# Location deviation in km: 95% minimal deviation, 5% significant outliers
loc_dev_low = np.random.exponential(scale=5, size=int(0.95 * num_transactions))
loc_dev_high = np.random.uniform(20, 100, size=int(0.05 * num_transactions))
location_deviation = np.concatenate([loc_dev_low, loc_dev_high])
np.random.shuffle(location_deviation)

# Create a DataFrame with rounded values
df = pd.DataFrame({
    "amount": np.round(amount, 2),
    "ip_distance": np.round(ip_distance, 2),
    "device_type_id": device_type_id,
    "time_of_day": np.round(time_of_day, 2),
    "tx_frequency": tx_frequency,
    "merchant_risk": np.round(merchant_risk, 2),
    "account_age": np.round(account_age, 2),
    "location_deviation": np.round(location_deviation, 2)
})

# Save the generated data to a CSV file
output_file = "transactions_sample.csv"
df.to_csv(output_file, index=False)
print(f"Sample transaction data generated and saved to '{output_file}'")
