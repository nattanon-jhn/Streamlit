import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime
import plotly.express as px

st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

#data
# Inspect the raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

# Histogram
st.subheader('Number of pickups by hour')
hist_values = np.histogram(
    data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

# Map
st.subheader('Map of all pickups')
st.map(data)

# Map with hour
hour_to_filter = 1
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
st.subheader(f'Map of all pickups at {hour_to_filter}:00')
st.map(filtered_data)

# 2D map Hour Slider
hour_to_filter = st.slider('hour', 0, 23, 17)  # min: 0h, max: 23h, default: 17h
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
st.subheader(f'2D Map of all pickups at {hour_to_filter}:00')
st.map(filtered_data)

# 3D map by PyDeck
st.subheader(f'3D Map of all pickups at {hour_to_filter}:00')
hour_to_filter = st.slider('hour', 0, 23, 17,key = 'hour_slider')  # min: 0h, max: 23h, default: 17h
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=40.73,
            longitude=-73.95,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=filtered_data,
                get_position="[lon, lat]",
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data=filtered_data,
                get_position="[lon, lat]",
                get_color="[200, 30, 0, 160]",
                get_radius=200,
            ),
        ],
    )
)

# Date input
st.subheader(f'Pickups with Date Input')
d = st.date_input("Select date", value=pd.to_datetime("2014-09-01").date(), format="YYYY-MM-DD")
filtered_data = data[data[DATE_COLUMN].dt.date == d]
filtered_data


# Selectbox
st.subheader(f'Pickups with Select Box')
date_options = sorted(data[DATE_COLUMN].dt.date.unique())
selected_date = st.selectbox(
    "What date do you want to see the pickups?",
    options=date_options,
    index=None,
    placeholder="Select date...",
    key="date_selectbox_data"
)
if selected_date:
    filtered_data = data[data[DATE_COLUMN].dt.date == selected_date]
    st.write(filtered_data)

# Plotly
st.subheader(f'Pickups with Plotly')
date_options = sorted(data[DATE_COLUMN].dt.date.unique())
selected_date = st.selectbox(
    "What date do you want to see the pickups?",
    options=date_options,
    placeholder="Select date...",
    key="date_selectbox_plotly"
)
# Bar Chart
if selected_date:
    filtered_data = data[data[DATE_COLUMN].dt.date == selected_date]
    st.write(f"📅 Showing data for: {selected_date}")
    # Add column 'hour' 
    filtered_data['hour'] = filtered_data[DATE_COLUMN].dt.hour

    # Bar Chart
    fig1 = px.bar(filtered_data.groupby('hour').size().reset_index(name='count'),
                  x='hour', y='count',
                  title='🚕 Number of Pickups per Hour',
                  labels={'count': 'Pickups', 'hour': 'Hour'})
    st.plotly_chart(fig1, use_container_width=True)

    # Scatter Plot
    fig2 = px.scatter_mapbox(filtered_data,
                             lat='lat', lon='lon',
                             hover_data=[DATE_COLUMN],
                             zoom=10, height=400,
                             title='🗺️ Pickup Locations (Map View)')
    fig2.update_layout(mapbox_style="carto-positron")
    fig2.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig2, use_container_width=True)

    # Line Chart
    filtered_data['minute'] = filtered_data[DATE_COLUMN].dt.floor('T')  # ปัดเวลาลงเป็นนาที
    trend_data = filtered_data.groupby('minute').size().cumsum().reset_index(name='cumulative_pickups')
    fig3 = px.line(trend_data,
                   x='minute', y='cumulative_pickups',
                   title='📈 Cumulative Pickups Over Time',
                   labels={'minute': 'Time', 'cumulative_pickups': 'Cumulative Pickups'})
    st.plotly_chart(fig3, use_container_width=True)


# Click a button to increase the number in the following message is increased,"This page has run 24 times"
# create state 
if "counter" not in st.session_state:
    st.session_state.counter = 0

st.subheader(f"This page has run {st.session_state.counter} times")

# Increase the number
if st.button("Click to increase the counter "):
    st.session_state.counter += 1