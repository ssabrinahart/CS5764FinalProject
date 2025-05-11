import os
import pandas as pd
import numpy as np
import zipfile
#define zip location 
zip_path = './MentalHealth/brff_datasets.zip'


# # Step 1: Unzip the dataset
# with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#     zip_ref.extractall('./MentalHealth/unzipped_files')

try:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('./MentalHealth/unzipped_files')
except zipfile.BadZipFile:
    print("The file is not a zip file or it is corrupted.")



# Define the base directory containing the year folders 
base_dir = './MentalHealth/unzipped_files/brff_datasets'
save_dir = './MentalHealth'
#cols to keep 
columns_needed = ["_STATE", "IMONTH", "IYEAR", "DISPCODE", "STATERE1", 
                  "GENHLTH", "PHYSHLTH", "MENTHLTH", "POORHLTH"]

# Initialize list to store all the filtered data
all_data = []
# Step 4: Filtering function
def filter_valid_vals(df):
    f2 = df[df['STATERE1'] == 1]
    f3 = f2[
        (f2['GENHLTH'].between(1, 30)) &
        (f2['PHYSHLTH'].between(1, 30)) &
        (f2['MENTHLTH'].between(1, 30)) &
        (f2['POORHLTH'].between(1, 30))
    ]
    return f3
# List the contents of the base directory (should contain year folders like 2023, 2022, etc.)
year_folders = os.listdir(base_dir)
print("Found the following year folders:", year_folders)

# Process each year folder
for year in year_folders:
    year_path = os.path.join(base_dir, year)
    
    # Check if the folder is a valid year folder (make sure it's a directory and its name is a number)
    if os.path.isdir(year_path) and year.isdigit():
        print(f"\nProcessing year folder: {year}")
        
        # Loop through files in the year folder
        for file in os.listdir(year_path):
            if file.endswith(".csv"):
                file_path = os.path.join(year_path, file)
                print(f"Processing file: {file_path}")
                
                try:
                    # Read the CSV file with the selected columns
                    df = pd.read_csv(file_path, usecols=columns_needed, low_memory=False)
                    
                    # Filter the data
                    filtered = filter_valid_vals(df)
                    print(f"Rows after filtering: {len(filtered)}")
                    
                    # If the data is not empty, add the year column and append to the all_data list
                    if not filtered.empty:
                        filtered["YEAR"] = int(year)
                        all_data.append(filtered)
                except Exception as e:
                    print(f"❌ Error with {file_path}: {e}")

# Step 4: Combine all dataframes if data exists
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    print("\n🎉 Final dataset preview:")
    print(final_df.head())
    print("Total records after filtering:", len(final_df))
else:
    print("No data matched filtering criteria.")

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

final_np = final_df.to_numpy()
# Convert column 0 (FIPS codes) from strings like '1.0' → float → int → str → zero-padded
fips_numeric = final_np[:,0].astype(float).astype(int)
fips_str = np.char.zfill(fips_numeric.astype(str), 2)

# Map FIPS codes to state abbreviations
state_names = np.vectorize(fips_to_abbrev.get)(fips_str)

# Append state names as a new column
data_with_states = np.column_stack((final_df, state_names))


# Assume column 6 is some float value (adjust if needed)
values = data_with_states[:, 6].astype(float)  # e.g., a depression rate or similar
states = data_with_states[:, -1]  # last column has state names
years = data_with_states[:, 2]  # e.g., year column
# Aggregate by state & year

# Unique combinations of state and year
unique_keys = np.unique(np.column_stack((states, years)), axis=0)


# Aggregate by (state, year)
aggregated_results = []
for state, year in unique_keys:
    mask = (states == state) & (years == year)
    mean_val = values[mask].mean()
    aggregated_results.append((state, year, mean_val))

# Convert aggregated results to a DataFrame
aggregated_df = pd.DataFrame(aggregated_results, columns=["State", "Year", "MenHealth_MeanValue"])

# Save to CSV
output_path = os.path.join(save_dir, "combined_mental_health_data_state_year_aggregated.csv")
aggregated_df.to_csv(output_path, index=False)

print(f"Final dataset saved to: {output_path}")
