
import numpy as np
from datetime import datetime

# Load the GPCP precipitation data

filepath = './gpcp_precip_cleaned.csv'

gpcpPrecipData = np.genfromtxt(filepath, delimiter=',', dtype=None, encoding='utf-8', names=True)
print(gpcpPrecipData.dtype.names)
# Extract relevant columns
dates = gpcpPrecipData['time']
states = gpcpPrecipData['STATE_NAME']
precip = gpcpPrecipData['precip']

# Extract year from date strings
years = np.array([datetime.strptime(date, '%Y-%m-%d').year for date in dates])

# Unique states and years
unique_states = np.unique(states)
unique_years = np.unique(years)

# Aggregate data: (state, year) → average precip
aggregated = []
for state in unique_states:
    for year in unique_years:
        mask = (states == state) & (years == year)
        if np.any(mask):
            avg = np.mean(precip[mask])
            aggregated.append((state, year, avg))

# Convert to structured array
aggregated_array = np.array(
    aggregated,
    dtype=[('state', 'U30'), ('year', 'i4'), ('avg_precip', 'f4')]
)

# Save to CSV
np.savetxt(
    'gpcp_precip_aggregated_by_state_year.csv',
    aggregated_array,
    delimiter=',',
    fmt='%s,%d,%.2f',
    header='State,Year,AvgPrecip',
    comments=''
)


