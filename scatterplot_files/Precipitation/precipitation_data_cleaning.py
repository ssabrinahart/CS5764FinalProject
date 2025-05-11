import zipfile
import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
import os
from shapely.geometry import Point

# Define paths

zip_path = './Precipitation/precipitation.zip'
extract_dir = './Precipitation/unzipped_nc_files'
shapefile_path = './Precipitation\cb_2018_us_state_20m\cb_2018_us_state_20m.shp'
output_csv = './Precipitation\gpcp_precip_cleaned.csv'

# Step 1: Unzip all .nc files
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Step 2: Load state polygons once
states = gpd.read_file(shapefile_path).to_crs("EPSG:4326")

# Step 3: Prepare for collection
all_data = []

# Step 4: Process each .nc file
for filename in os.listdir(extract_dir):
    if filename.endswith('.nc'):
        file_path = os.path.join(extract_dir, filename)
        ds = xr.open_dataset(file_path)

        data_var = ds['precip']  # Update if variable name differs
        df = data_var.to_dataframe().reset_index()

        # Fix longitudes
        df['longitude'] = df['longitude'].apply(lambda x: x - 360 if x > 180 else x)

        # Drop NaNs
        df = df.dropna(subset=['precip'])

        # GeoDataFrame setup
        df['geometry'] = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

        # Spatial join with states
        gdf = gpd.sjoin(gdf, states, how='left', predicate='within')

        # Filter to valid points in U.S.
        gdf = gdf[gdf['STATEFP'].notna()]
        gdf = gdf.rename(columns={'STATEFP': 'state_code', 'STUSPS': 'state_abbr', 'NAME': 'STATE_NAME'})

        # Group by time and state
        grouped = gdf.groupby(['time', 'state_abbr'])['precip'].mean().reset_index()
        all_data.append(grouped)

# Step 5: Combine everything & save

final_df = pd.concat(all_data, ignore_index=True)
final_df.to_csv(output_csv, index=False)

# print(f"Saved {len(final_df)} rows to {output_csv}")
# print(f"{len(final_df['STATE_NAME'].unique())} unique states found.")