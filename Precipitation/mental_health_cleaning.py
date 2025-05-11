import numpy as np
import matplotlib.pyplot as plt

# Load your CSV (assuming FIPS codes are in column 0 as floats like 1.0)
mentalHealthData = np.genfromtxt('./combined_mental_health_data.csv', delimiter=',', skip_header=1, dtype=str, encoding='utf-8')

filepath = './gpcp_precip_cleaned.csv'
gpcpPrecipData = np.genfromtxt(filepath, delimiter=',', skip_header=1, dtype=None, encoding='utf-8', ndmin=2)

# Ensure the data has the expected number of columns
# Accessing the values of the numpy array
print(gpcpPrecipData.dtype.names)
fips_to_abbrev = {
    '01': 'AL',
    '02': 'AK',
    '04': 'AZ',
    '05': 'AR',
    '06': 'CA',
    '08': 'CO',
    '09': 'CT',
    '10': 'DE',
    '11': 'DC',
    '12': 'FL',
    '13': 'GA',
    '15': 'HI',
    '16': 'ID',
    '17': 'IL',
    '18': 'IN',
    '19': 'IA',
    '20': 'KS',
    '21': 'KY',
    '22': 'LA',
    '23': 'ME',
    '24': 'MD',
    '25': 'MA',
    '26': 'MI',
    '27': 'MN',
    '28': 'MS',
    '29': 'MO',
    '30': 'MT',
    '31': 'NE',
    '32': 'NV',
    '33': 'NH',
    '34': 'NJ',
    '35': 'NM',
    '36': 'NY',
    '37': 'NC',
    '38': 'ND',
    '39': 'OH',
    '40': 'OK',
    '41': 'OR',
    '42': 'PA',
    '44': 'RI',
    '45': 'SC',
    '46': 'SD',
    '47': 'TN',
    '48': 'TX',
    '49': 'UT',
    '50': 'VT',
    '51': 'VA',
    '53': 'WA',
    '54': 'WV',
    '55': 'WI',
    '56': 'WY',
    '60': 'AS',  # American Samoa
    '66': 'GU',  # Guam
    '69': 'MP',  # Northern Mariana Islands
    '72': 'PR',  # Puerto Rico
    '74': 'UM',  # U.S. Minor Outlying Islands
    '78': 'VI'   # U.S. Virgin Islands
}


# Convert column 0 (FIPS codes) from strings like '1.0' → float → int → str → zero-padded
fips_numeric = mentalHealthData[:, 0].astype(float).astype(int)
fips_str = np.char.zfill(fips_numeric.astype(str), 2)

# Map FIPS codes to state names
state_names = np.vectorize(fips_to_abbrev.get)(fips_str)

# Append state names as a new column
data_with_states = np.column_stack((mentalHealthData, state_names))


# Assume column 6 is some float value (adjust if needed)
values = data_with_states[:, 6].astype(float)  # e.g., a depression rate or similar
states = data_with_states[:, -1]  # last column has state names

# Aggregate by state
unique_states = np.unique(states)
avg_values = np.array([
    values[states == state].astype(float).mean() for state in unique_states
])

# Basic Plot - think i still need to clean up the data a bit more - remove outlier vals?
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
axes[0].bar(unique_states, avg_values, color='blue')
axes[0].set_xticklabels(unique_states, rotation=90)
axes[0].set_title("Average Mental Health Value by State")
axes[0].set_xlabel("State")
axes[0].set_ylabel("Average Value")

print("column names: ", gpcpPrecipData.dtype.names)
# Extract fields
gpcp_states = gpcpPrecipData['f1']
gpcp_precip = gpcpPrecipData['f2']

# Aggregate precipitation by state + year
unique_gpcp_states = np.unique(gpcp_states)
avg_precipitation = np.array([
    gpcp_precip[gpcp_states == state].mean() for state in unique_gpcp_states
])

# Plot

axes[1].bar(unique_gpcp_states, avg_precipitation, color='green')
axes[1].set_xticks(np.arange(len(unique_gpcp_states)))
axes[1].set_xticklabels(unique_gpcp_states, rotation=90)
axes[1].set_title("Average GPCP Precipitation by State (2018–2023)")
axes[1].set_xlabel("State")
axes[1].set_ylabel("Avg Precipitation (mm)")
plt.tight_layout()
# Save the figure if needed
fig.savefig('mental_health_vs_precipitation.png', dpi=300, bbox_inches='tight')

# Save the data with state names to a new CSV file
np.savetxt('./mental_health_data_with_states.csv', data_with_states, delimiter=',', fmt='%s', header="FIPS,State,Value", comments='')
