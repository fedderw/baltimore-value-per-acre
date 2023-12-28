import streamlit as st
import pydeck as pdk
from data_fetcher import get_total_count, fetch_and_process_data

# Base URL and necessary fields
base_url = "https://geodata.baltimorecity.gov/egis/rest/services/CityView/Realproperty_OB/FeatureServer/0/query"
fields = ['TAXBASE', 'geometry']
max_records = 1000

# Cached data fetching function
@st.cache_data
def get_data():
    count_url = f"{base_url}?where=1%3D1&returnCountOnly=true&f=json"
    total_count = get_total_count(count_url)
    return fetch_and_process_data(total_count, fields, base_url, max_records)

# Streamlit application main function
def main():
    st.title("Property Value-Per-Acre Map")

    # Fetching and processing data
    data = get_data()

    # Creating a map with PyDeck
    view_state = pdk.ViewState(latitude=38.9072, longitude=-77.0369, zoom=10)
    layer = pdk.Layer(
        'GeoJsonLayer',
        data,
        get_fill_color='[255, 255, 255, (tax_value_per_acre / max_tax_value_per_acre) * 255]',
        pickable=True
    )
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# Running the Streamlit app
if __name__ == "__main__":
    main()
