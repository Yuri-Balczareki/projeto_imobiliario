import pandas as pd
from geopy.geocoders import Nominatim
import time
import json
from geopy.exc import GeocoderUnavailable  # Add this import


def geocode_missing_coordinates(json_file_path, start_index, final_index, save_path_json):
    # Function to geocode zip code and return latitude and longitude
    def get_lat_long_from_zip(zip_code):
        geolocator = Nominatim(user_agent="geoapi")
        retries = 3  # Number of retries
        delay = 1  # Delay in seconds between retries
        for _ in range(retries):
            try:
                location = geolocator.geocode(zip_code)
                if location:
                    return location.latitude, location.longitude
            except GeocoderUnavailable as e:
                print(f"Error: {e}")
                # Save DataFrame to JSON before raising the exception
                df.to_json(save_path_json, orient='records')
                raise e
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(delay)  # Retry after delay
        return None, None

    # Load DataFrame from JSON file
    with open(json_file_path, 'r') as f:
        df = pd.read_json(f)

    # Counter for missing latitude and longitude
    missing_counter = 0

    # Total number of rows to process
    total_rows = final_index - start_index + 1

    # Iterate over DataFrame rows within the specified range
    for i, (index, row) in enumerate(df.iloc[start_index:final_index+1].iterrows(), start=start_index):
        # Check if either latitude or longitude is missing
        if pd.isna(row['address.point.lat']) or pd.isna(row['address.point.lon']):
            # Get latitude and longitude from zip code
            latitude, longitude = get_lat_long_from_zip(row['address.zipCode'])
            # If latitude and longitude are available, update the row
            if latitude is not None and longitude is not None:
                df.at[index, 'address.point.lat'] = latitude
                df.at[index, 'address.point.lon'] = longitude
            else:
                # Try to geocode using address information
                if pd.notna(row['address.street']):
                    geolocator = Nominatim(user_agent="geoapi")
                    location = geolocator.geocode(row['address.street'])
                    if location:
                        latitude, longitude = location.latitude, location.longitude
                        df.at[index, 'address.point.lat'] = latitude
                        df.at[index, 'address.point.lon'] = longitude
                    else:
                        missing_counter += 1
                else:
                    missing_counter += 1
        
        # Calculate percentage completion
        completion_percentage = (i / total_rows) * 100
        print(f"Progress: {completion_percentage:.2f}%")

    # Print the number of rows with missing latitude and longitude
    print(f"Total missing coordinates: {missing_counter}")

    # Save the DataFrame as JSON
    df.to_json(save_path_json, orient='records')

# Example usage:
json_file_path = 'data/Florianopolis/florianopolis/Buy/treated/buy_treated_lat_long.json'
save_path_json = 'data/Florianopolis/florianopolis/Buy/treated/buy_treated_lat_long.json'
start_index = 70000                                            
final_index = 78960   # For example, specify the final index you want to process
geocode_missing_coordinates(json_file_path, start_index, final_index, save_path_json)
                