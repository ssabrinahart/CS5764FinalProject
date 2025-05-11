import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go

class ScatterplotVisualizer:
    def __init__(self, precipitation_df, mental_health_df, decoder_df,
                 title="Precipitation ↔ Mental Health (MH) Heatmap", cmap="greys"):
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
                  colorscale=None,
                  size_range=(10, 50)):
        """
        If as_scatter=True, draw a scatterplot:
          • x = Month
          • y = precip (mm/day)
          • marker.size ~ MENTHLTH (scaled to `size_range`)
          • marker.color  ~ MENTHLTH (optional, shows colorbar)
        Otherwise draws the 2D heatmap as before.
        """
        df = self.combined_df.copy()
        df_year = df[df['time'].dt.year == year].copy()

        # US‐aggregate vs state
        if state.upper() == 'US':
            df_plot = (df_year
                       .groupby('time')[['precip','MENTHLTH']]
                       .mean().reset_index())
        else:
            df_plot = df_year[df_year['state_abbr'] == state.upper()].copy()

        # bail if no data
        if df_plot.empty or df_plot[['precip','MENTHLTH']].dropna().empty:
            return None

        # add Month column
        df_plot['Month'] = df_plot['time'].dt.month_name().str[:3]
        month_order = ['Jan','Feb','Mar','Apr','May','Jun',
                       'Jul','Aug','Sep','Oct','Nov','Dec']
        df_plot['Month'] = pd.Categorical(df_plot['Month'],
                                          categories=month_order,
                                          ordered=True)

        # --- SCATTER PATH ---
        # scale mental‐health days to marker sizes
        scaler = MinMaxScaler(feature_range=size_range)
        # reshape for scaler
        mh_vals = df_plot['MENTHLTH'].to_numpy().reshape(-1,1)
        sizes  = scaler.fit_transform(mh_vals).flatten()

        fig = go.Figure(go.Scatter(
            x=df_plot['Month'],
            y=df_plot['precip'],
            mode='markers',
            marker=dict(
                size=sizes,
                color=df_plot['MENTHLTH'],
                colorscale=colorscale or self.cmap,
                showscale=True,
                colorbar=dict(title="Avg Poor MH Days")
            ),
            hovertemplate=(
                "Month: %{x}<br>"
                "Precip: %{y:.2f} mm/day<br>"
                "Avg MH Days: %{marker.color:.1f}<extra></extra>"
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