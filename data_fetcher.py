import requests
import geopandas as gpd
import pandas as pd
from tqdm import tqdm

# Base URL and necessary fields for fetching property data
fields = ['TAXBASE', 'geometry']
base_url = "https://geodata.baltimorecity.gov/egis/rest/services/CityView/Realproperty_OB/FeatureServer/0/query"
max_records = 1000  # Maximum number of records per query as set by the server

# Function to get the total count of records
def get_total_count(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    return response.json()['count']

# Function to fetch and process data in chunks
def fetch_and_process_data(total_count, fields, base_url, max_records):
    all_data = pd.DataFrame()
    for offset in tqdm(range(0, total_count, max_records), desc="Processing Records"):
        query_params = {
            'outFields': ','.join(fields),
            'where': '1=1',
            'f': 'geojson',
            'resultOffset': offset,
            'resultRecordCount': max_records
        }
        query_url = f"{base_url}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"
        chunk_gdf = gpd.read_file(query_url)
        chunk_gdf = chunk_gdf.to_crs('EPSG:2248')  # Reproject to a suitable CRS
        chunk_gdf['area_sqm'] = chunk_gdf['geometry'].area
        chunk_gdf['tax_value_per_acre'] = chunk_gdf.apply(
            lambda row: row['TAXBASE'] / (row['area_sqm'] * 0.000247105) if row['area_sqm'] > 0 else None, axis=1)
        all_data = pd.concat([all_data, chunk_gdf], ignore_index=True)
    return all_data

# Main execution block
if __name__ == "__main__":
    count_url = f"{base_url}?where=1%3D1&returnCountOnly=true&f=json"
    total_count = get_total_count(count_url)
    data = fetch_and_process_data(total_count, fields, base_url, max_records)
    print(len(data))
    print(data[['TAXBASE', 'area_sqm', 'tax_value_per_acre']].head(5))
