# HeatmapVisualizer

A Python class for creating interactive Plotly heatmaps that illustrate the monthly relationship between precipitation and poor mental-health days for U.S. states (or the entire U.S.).

---

## Overview

`HeatmapVisualizer` takes three pandas DataFrames:

1. **precipitation\_df**: Contains daily or monthly precipitation values with columns:

   * `time` (datetime string or `datetime64[ns]`)
   * `state_abbr` (two-letter USPS state code)
   * `precip` (numeric precipitation amount)

2. **mental\_health\_df**: Contains survey data aggregated by state, year, and month with columns:

   * `IYEAR` (integer year)
   * `IMONTH` (integer month, 1–12)
   * `MENTHLTH` (numeric: days of poor mental health)
   * `_STATE` (numeric state FIPS code)

3. **decoder\_df**: Lookup table to map `_STATE` FIPS code → `Abbreviation` (two-letter state code) with columns:

   * `_STATE` (numeric)
   * `Abbreviation` (string USPS code)

The class merges and aligns these DataFrames on the first day of the month and state code, producing a combined DataFrame ready for visualization.

---

## Class Interface

### `__init__(precipitation_df, mental_health_df, decoder_df, title, cmap)`

* **Parameters**:

  * `precipitation_df` (`pd.DataFrame`): Precipitation data.
  * `mental_health_df` (`pd.DataFrame`): Mental health survey data.
  * `decoder_df` (`pd.DataFrame`): State code decoder.
  * `title` (`str`, optional): Base title for visualizations. Defaults to `"Precipitation ↔ Mental Health Heatmap"`.
  * `cmap` (`str`, optional): Plotly colorscale for heatmap. Defaults to `'Blues'`.

* **Behavior**:

  1. Calls `normalize_and_combine` to merge and align data.
  2. Stores the combined DataFrame in `self.combined_df`.

### `normalize_and_combine(precipitation_df, mental_health_df, decoder_df) -> pd.DataFrame`

* **Purpose**: Preprocess and merge the raw input DataFrames into a single monthly, state-level DataFrame.

* **Steps**:

  1. Converts `IYEAR`/`IMONTH` to a `time` datetime at month start.
  2. Filters mental health rows by valid `_STATE` codes.
  3. Merges with `decoder_df` to get `state_abbr`.
  4. Parses precipitation `time`, truncates both to monthly periods.
  5. Performs a left-join on `time` and `state_abbr`.

* **Returns**: `pd.DataFrame` with columns:

  * `time` (`datetime64[ns]`, month start)
  * `state_abbr` (string)
  * `MENTHLTH` (numeric)
  * `precip` (numeric)

### `visualize(year, state='US', n_bins=10, binning=False, colorscale=None) -> plotly.graph_objects.Figure or None`

Generate a heatmap for a given year and state.

* **Parameters**:

  * `year` (`int`): Four-digit year to visualize.
  * `state` (`str`): Two-letter USPS code or `'US'` for national aggregate. Case-insensitive.
  * `n_bins` (`int`): Number of precipitation bins (only used if `binning=True`).
  * `binning` (`bool`): Whether to bucket precipitation values (`True`) or use raw per-month values (`False`).
  * `colorscale` (`str`, optional): Plotly colorscale name. If omitted, uses `self.cmap`.

* **Behavior**:

  1. Filters `self.combined_df` to rows matching `year` and `state`.
  2. Returns `None` if no rows or all values missing for precipitation or mental health.
  3. Extracts short month names (`Jan`, `Feb`, …) and orders them chronologically.
  4. If `binning=True`, bins precipitation into `n_bins` and aggregates.
     Otherwise, pivots directly on raw precipitation values.
  5. Constructs a `go.Figure` heatmap:

     * **X-axis**: Month
     * **Y-axis**: Precipitation (bins or raw values)
     * **Color**: Average `MENTHLTH`
     * **Hover**: Shows precipitation, month, and avg mental health days

* **Returns**:

  * `plotly.graph_objects.Figure`: A fully configured heatmap plot.
  * `None`: If filtered data is empty or missing.

---

## Example Usage

```python
import pandas as pd
from visualizer import HeatmapVisualizer

# Load data
precip_df = pd.read_csv('gpcp_precip_cleaned.csv')
mh_df     = pd.read_csv('combined_mental_health.csv')
decoder   = pd.read_csv('state_decoder.csv')

# Instantiate\ n
viz = HeatmapVisualizer(precip_df, mh_df, decoder,
                         title='Monthly Precip ↔ Poor MH Days', cmap='Viridis')

# Generate for California in 2020 without binning
fig = viz.visualize(year=2020, state='CA', binning=False)

# Show in Jupyter
fig.show()
```

---

## Error Handling

* If the filtered data for a given `(year, state)` has no precipitation or mental-health values, `visualize` returns `None`. Consumers (e.g., Streamlit apps) should check for `None` before rendering.

---