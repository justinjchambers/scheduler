import googlemaps
import pandas as pd
import time
import os

data_directory = '/Users/justinchambers/Desktop/Programming/MLS/Schedule/data'
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# set up the Google Maps API client
gmaps = googlemaps.Client(key='AIzaSyAjBn8FuWH6TosSpmJpU-elbSebe9XhPQo')

# read the CSV file containing the venues data
venues = pd.read_csv(
    '/Users/justinchambers/Desktop/Programming/MLS/Schedule/data/venues.csv')

# define a function to get the travel time between two locations


def get_travel_time(origin_lat, origin_lon, dest_lat, dest_lon):
    # format the origin and destination coordinates
    origin = f"{origin_lat},{origin_lon}"
    destination = f"{dest_lat},{dest_lon}"

    # make the API request
    result = gmaps.distance_matrix(
        origin, destination, mode="driving", departure_time="now")

    # parse the duration from the response
    duration = result['rows'][0]['elements'][0]['duration']['value'] / 3600

    # wait for a short period to avoid hitting the API rate limit
    time.sleep(0.1)

    return duration


# create an empty DataFrame to store the travel times
bus_travel_times = pd.DataFrame(index=venues['name'], columns=venues['name'])

for i, row1 in venues.iterrows():
    for j, row2 in venues.iterrows():
        if i < j:
            origin_lat = row1['latitude']
            origin_lon = row1['longitude']
            dest_lat = row2['latitude']
            dest_lon = row2['longitude']
            travel_time = get_travel_time(
                origin_lat, origin_lon, dest_lat, dest_lon)
            bus_travel_times.loc[row1['name'], row2['name']] = travel_time
            bus_travel_times.loc[row2['name'], row1['name']] = travel_time

# save the travel times to a CSV file
output_file = '/Users/justinchambers/Desktop/Programming/MLS/Schedule/data/bus_travel_time.csv'
bus_travel_times.to_csv(output_file, index_label='name', float_format='%.2f')
print(f'Travel times saved to {output_file}')
