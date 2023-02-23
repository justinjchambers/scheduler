import csv
from math import radians, sin, cos, sqrt, atan2

# Earth's radius in km
EARTH_RADIUS = 6371

# Read the airports from the CSV file
airports = []
with open('data/airports.csv') as file:
    reader = csv.DictReader(file)
    for row in reader:
        airports.append(row)

# Calculate the travel times between airports and write to a CSV file
with open('data/air_travel_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Write header row
    writer.writerow(['Origin', 'Destination', 'Travel Time (hrs)'])
    for i, airport1 in enumerate(airports):
        for airport2 in airports[i+1:]:
            # Calculate the distance between the airports using the Haversine formula
            lat1, lon1 = radians(float(airport1['latitude'])), radians(
                float(airport1['longitude']))
            lat2, lon2 = radians(float(airport2['latitude'])), radians(
                float(airport2['longitude']))
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = EARTH_RADIUS * c

            # Calculate the travel time based on a constant speed of 700 km/hr
            travel_time = distance / 700.0
            writer.writerow(
                [airport1['iata_code'], airport2['iata_code'], travel_time])
