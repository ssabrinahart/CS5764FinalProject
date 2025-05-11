import streamlit as st
import pandas as pd
import plotly.express as px
from scatterplot_files.scatterplot import ScatterplotVisualizer
from choropleth_files.choropleth import choropleth_combined, choropleth_mental, choropleth_precip

# Title
st.title("CS5764 Final Project: How does Weather Impact Mental Health")


# Sidebar for user interaction
chart_type = st.sidebar.selectbox("Select Visualization", [
                                                           "Choropleth - Precipitation", 
                                                           "Choropleth - Mental Health", 
                                                           "Choropleth - Combined",
                                                           "Monthly Precipitation"
                                                           ])
# Load data
precip_df = pd.read_csv('./cleaningOutput/gpcp_precip_cleaned.csv')
mh_df     = pd.read_csv('./cleaningOutput/combined_mental_health_data.csv')
decoder   = pd.read_csv('./cleaningOutput/state_codes.csv')
chlor_data = pd.read_csv('./choropleth_files/cleaningOutput/combined_mental_health_data_state_year_aggregated.csv')

selected_state = ''
selected_year = ''

# Plotly visualizations
if chart_type == "Monthly Precipitation":

    state_options = decoder['Abbreviation'].sort_values().unique()
    selected_state = st.sidebar.selectbox("Select State", state_options)

    year_options = mh_df['IYEAR'].sort_values().unique()
    selected_year = st.sidebar.selectbox("Select Year", year_options)

    # Instantiate visualizer
    viz = ScatterplotVisualizer(
        precip_df, mh_df.sort_values(by='IMONTH'), decoder,
        title='Monthly Precip vs. Poor Mental Heath Days',
        cmap='Cividis'
    )

    # Create scatter for Washington in 2018
    fig = viz.visualize(
        year=selected_year,
        state=selected_state,
        colorscale='blues',
        size_range=(15, 30)
    )
elif chart_type == "Choropleth - Precipitation":
    year_options = chlor_data['Year'].sort_values().unique()
    selected_year = st.sidebar.selectbox("Select Year", list(map(int, year_options[:-1])))
    fig = choropleth_precip(int(selected_year))

elif chart_type == "Choropleth - Mental Health":
    year_options = chlor_data['Year'].sort_values().unique()
    selected_year = st.sidebar.selectbox("Select Year", list(map(int, year_options[:-1])))
    fig = choropleth_mental(selected_year)

elif chart_type == "Choropleth - Combined":
    year_options = chlor_data['Year'].sort_values().unique()
    selected_year = st.sidebar.selectbox("Select Year", list(map(int, year_options[:-1])))
    fig = choropleth_combined(selected_year)

# Display Plotly figure
if fig:
    st.plotly_chart(fig)
else:
    if chart_type == "Monthly Precipitation":
        st.warning(f'No data available for this {selected_state} in year {selected_year}. Please select a different option.')


# Visualization Captions
if fig: 
    if chart_type == "Monthly Precipitation":
        st.write(f'''Monthly precipitation (mm/day) vs. average days of poor mental health in {selected_state}, {selected_year}. 
                Each circle’s size and color intensity encode the mean number of self-reported poor mental-health days.''')
    elif chart_type == "Choropleth - Precipitation":
        st.write(f'Average monthly precipitation in mm year {selected_year}')

    elif chart_type == "Choropleth - Mental Health":
        st.write(f'Average number of days individuals feel depressed or down per month by state in year {selected_year} ')

    elif chart_type == "Choropleth - Combined":
        st.write(f'''Average precipitation and the average number of days individuals feel depressed/down in a year {selected_year}. 
                 Precipitation is shown by the color of the state and the number of days down/depressed are shown by 
                 the size of the overlayed dot.''')

if fig:
    # Optionally show the dataframe
    # Visualization Captions
    if chart_type == "Monthly Precipitation":
        if st.checkbox("Show DataFrame Head"):
            st.write('Precipitation Data') 
            st.write(precip_df[precip_df['state_abbr'] == selected_state].reset_index(drop=True).head()) 
            st.write('Mental Health Data') 
            st.write(mh_df[mh_df['IYEAR'] == selected_year].reset_index(drop=True).head())

    elif chart_type == "Choropleth - Mental Health" or chart_type == "Choropleth - Combined":
        if st.checkbox("Show DataFrame Head"):
            st.write(chlor_data[chlor_data['Year'] == selected_year].reset_index(drop=True).head())


