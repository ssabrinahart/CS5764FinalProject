import pandas as pd
import plotly.graph_objects as go

class HeatmapVisualizer:
    def __init__(self, precipitation_df, mental_health_df, decoder_df,
                 title="Precipitation ↔ Mental Health (MH) Heatmap", cmap="Blues"):
        # Store provided dataframes and compute the combined normalized dataframe
        self.precipitation_df = precipitation_df
        self.mental_health_df = mental_health_df
        self.decoder_df = decoder_df
        self.combined_df = self.normalize_and_combine(
            self.precipitation_df, self.mental_health_df, self.decoder_df
        )
        self.title = title
        self.cmap = cmap

    def normalize_and_combine(self, precipitation_df, mental_health_df, decoder_df):
        # Convert mental health data year and month into a datetime column
        mental_health_df['Date'] = pd.to_datetime(
            dict(year=mental_health_df.IYEAR, month=mental_health_df.IMONTH, day=1)
        )
        # Filter and select the required mental health columns
        mh_df_filtered = mental_health_df[['Date', 'MENTHLTH', '_STATE']]
        mh_df_filtered = mh_df_filtered[mh_df_filtered['_STATE'].isin(decoder_df['_STATE'])]
        # Merge with the decoder for state abbreviation
        mh_df_filtered = mh_df_filtered.merge(decoder_df, on='_STATE', how='left')
        # Rename columns for consistency
        mh_df_filtered = mh_df_filtered.rename(
            columns={
                'Date': 'time',
                'Abbreviation': 'state_abbr',
            }
        )
        # Convert precipitation time column to datetime format
        precipitation_df['time'] = pd.to_datetime(precipitation_df['time'], format='%Y-%m-%d')

        # Ensure both dataframes have matching monthly timestamps
        for df in (mh_df_filtered, precipitation_df):
            df['time'] = pd.to_datetime(df['time'])
            df['time'] = df['time'].dt.to_period('M').dt.to_timestamp()

        # Merge dataframes on time and state abbreviation
        merged = pd.merge(
            mh_df_filtered,
            precipitation_df,
            on=['time', 'state_abbr'],
            how='left',
            suffixes=('_mental_health', '_precipitation')
        )

        return merged

    def visualize(self,
                  year,
                  state='US',
                  n_bins=10,
                  binning=False,
                  colorscale=None):
        """
        year    : int
        state   : 'US' or two-letter code
        n_bins  : only used if binning=True
        binning : if False, we pivot on raw precip values
        """
        df = self.combined_df.copy()
        df_year = df[df['time'].dt.year == year].copy()

        # aggregate for US or filter for a single state
        if state.upper() == 'US':
            df_plot = (df_year
                       .groupby('time')[['precip','MENTHLTH']]
                       .mean()
                       .reset_index()).copy()
        else:
            df_plot = df_year[df_year['state_abbr'] == state.upper()].copy()

        if df_plot.empty or df_plot['precip'].notna().sum() == 0 or df_plot['MENTHLTH'].notna().sum() == 0:
            return None

        # month names in calendar order
        df_plot['Month'] = df_plot['time'].dt.month_name().str[:3]
        month_order = ['Jan','Feb','Mar','Apr','May','Jun',
                       'Jul','Aug','Sep','Oct','Nov','Dec']
        df_plot['Month'] = pd.Categorical(df_plot['Month'],
                                          categories=month_order,
                                          ordered=True)

        if binning:
            # --- your existing code ---
            df_plot['precip_bin'] = pd.cut(df_plot['precip'], bins=n_bins)
            agg = (df_plot
                   .groupby(['precip_bin','Month'], observed=False)['MENTHLTH']
                   .mean()
                   .reset_index(name='avg_menthlth'))
            mat = agg.pivot(index='precip_bin',
                            columns='Month',
                            values='avg_menthlth')
            y_labels = [f"{iv.left:.0f}–{iv.right:.0f}" for iv in mat.index]
        else:
            # pivot on the raw precipitation values
            mat = df_plot.pivot_table(
                index = 'precip',
                columns = 'Month',
                values = 'MENTHLTH',
                aggfunc = 'mean',
                observed=False
            )
            # use the numeric precip values as y-labels
            y_labels = [f"{p:.1f}" for p in mat.index]

        # build the heatmap
        fig = go.Figure(go.Heatmap(
            z=mat.values,
            x=mat.columns,
            y=y_labels,
            colorscale=colorscale or self.cmap,
            colorbar=dict(title="Avg Poor MH Days"),
            hovertemplate=(
                "Precip: %{y} mm<br>"
                "Month: %{x}<br>"
                "Avg Poor MH Days: %{z:.2f}<extra></extra>"
            )
        ))

        fig.update_layout(
            title=f"{self.title} — {state.upper()} {year}",
            xaxis_title="Month",
            yaxis_title="Precipitation (mm/day)",
            xaxis_tickangle=-45,
            height=400
        )
        return fig