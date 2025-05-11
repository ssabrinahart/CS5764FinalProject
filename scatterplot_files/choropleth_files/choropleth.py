import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


precip = pd.read_csv('./cleaningOutput/gpcp_precip_cleaned.csv')
mental = pd.read_csv('./cleaningOutput/combined_mental_health_data_state_year_aggregated.csv')

def choropleth_precip(year): 
    precip['time'] = pd.to_datetime(precip['time'], format='%Y-%m-%d')
     # Filter data for the specified year
    data_year = precip[precip['time'].dt.year == year].copy()
    

    fig = px.choropleth(data_year,
                        locations='state_abbr',
                        locationmode='USA-states',
                        color='precip',
                        hover_name='state_abbr',
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title=f"Average GPCP Precipitation (mm/day) in {year}",
                        scope='usa'
                    )
    fig.update_layout(coloraxis_colorbar=dict(title="Precipitation (mm/day)"))
    #fig.show()
    return fig

#choropleth_precip(2018)

def choropleth_mental(year):
    mental['Year'] = pd.to_datetime(mental['Year'], format='%Y')
    # Filter data for the specified year
    data_year = mental[mental['Year'].dt.year == year].copy()
    
    fig = px.choropleth(data_year,
                        locations='State',
                        locationmode='USA-states',
                        color='MenHealth_MeanValue',
                        hover_name='State',
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title=f"Average Mental Health in {year}",
                        scope='usa'
                    )
    fig.update_layout(coloraxis_colorbar=dict(title="Avg. Poor Mental Health Days"))
    #fig.show()
    return fig

# Example: precomputed state centroids (latitude/longitude) for the 50 U.S. states
state_centroids = {
    'AL': (32.806671, -86.791130),
    'AK': (61.370716, -152.404419),
    'AZ': (33.729759, -111.431221),
    'AR': (34.969704, -92.373123),
    'CA': (36.116203, -119.681564),
    'CO': (39.059811, -105.311104),
    'CT': (41.597782, -72.755371),
    'DE': (39.318523, -75.507141),
    'FL': (27.766279, -81.686783),
    'GA': (33.040619, -83.643074),
    'HI': (21.094318, -157.498337),
    'ID': (44.240459, -114.478828),
    'IL': (40.349457, -88.986137),
    'IN': (39.849426, -86.258278),
    'IA': (42.011539, -93.210526),
    'KS': (38.526600, -96.726486),
    'KY': (37.668140, -84.670067),
    'LA': (31.169546, -91.867805),
    'ME': (44.693947, -69.381927),
    'MD': (39.063946, -76.802101),
    'MA': (42.230171, -71.530106),
    'MI': (43.326618, -84.536095),
    'MN': (45.694454, -93.900192),
    'MS': (32.741646, -89.678696),
    'MO': (38.456085, -92.288368),
    'MT': (46.921925, -110.454353),
    'NE': (41.125370, -98.268082),
    'NV': (38.313515, -117.055374),
    'NH': (43.452492, -71.563896),
    'NJ': (40.298904, -74.521011),
    'NM': (34.840515, -106.248482),
    'NY': (42.165726, -74.948051),
    'NC': (35.630066, -79.806419),
    'ND': (47.528912, -99.784012),
    'OH': (40.388783, -82.764915),
    'OK': (35.565342, -96.928917),
    'OR': (44.572021, -122.070938),
    'PA': (40.590752, -77.209755),
    'RI': (41.680893, -71.511780),
    'SC': (33.856892, -80.945007),
    'SD': (44.299782, -99.438828),
    'TN': (35.747845, -86.692345),
    'TX': (31.054487, -97.563461),
    'UT': (40.150032, -111.862434),
    'VT': (44.045876, -72.710686),
    'VA': (37.769337, -78.169968),
    'WA': (47.400902, -121.490494),
    'WV': (38.491226, -80.954578),
    'WI': (44.268543, -89.616508),
    'WY': (42.755966, -107.302490)
}

def choropleth_combined(year):
    # Filter and parse date columns
    precip['time'] = pd.to_datetime(precip['time'], format='%Y-%m-%d')
    data_year_precip = precip[precip['time'].dt.year == year].copy()

    mental['Year'] = pd.to_datetime(mental['Year'], format='%Y')
    data_year_mental = mental[mental['Year'].dt.year == year].copy()

    # Merge datasets on state abbreviation
    merged = pd.merge(data_year_precip, data_year_mental, left_on='state_abbr', right_on='State', how='inner')

    # Get coordinates for each state
    merged['lat'] = merged['state_abbr'].map(lambda x: state_centroids.get(x, (None, None))[0])
    merged['lon'] = merged['state_abbr'].map(lambda x: state_centroids.get(x, (None, None))[1])

    # Normalize and scale dot size
    min_size = 5
    max_size = 25
    mh_values = merged['MenHealth_MeanValue'].astype(float)
    mh_scaled = (mh_values - mh_values.min()) / (mh_values.max() - mh_values.min())
    dot_sizes = mh_scaled * (max_size - min_size) + min_size

    # Choropleth: precipitation
    fig = px.choropleth(
        merged,
        locations='state_abbr',
        locationmode='USA-states',
        color='precip',
        scope='usa',
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"Average Precipitation (mm/day) & Mental Health in {year}"
    )

    # Scatter: dot size = mental health
    fig.add_trace(go.Scattergeo(
    locationmode='USA-states',
    lat=merged['lat'],
    lon=merged['lon'],
    text=merged['state_abbr'] + "<br>Mental Health: " + merged['MenHealth_MeanValue'].astype(str),
    marker=dict(
        size=dot_sizes,
        color='black',
        opacity=0.5,
        symbol='circle'
    ),
    name='Mental Health Value'
))


    fig.update_layout(legend_title_text='Precipitation (Color), Mental Health (Dot Size)', geo=dict(scope='usa'))
    fig.update_layout(coloraxis_colorbar=dict(title="Precipitation (mm/day)"))
    #fig.show()
    return fig


choropleth_combined(2018)