import pandas as pd
from math import radians, cos, sin, asin, sqrt

# read the CSV file
df = pd.read_csv(
    'data/venues.csv')

# define the Haversine formula to compute the distance between two coordinates


def haversine(lat1, lon1, lat2, lon2):
    R = 6372.8  # Earth radius in kilometers

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))

    return R*c


# initialize the distance matrix with NaN values
dist_matrix = pd.DataFrame(index=df['name'], columns=df['name'])
dist_matrix[:] = float('nan')

# iterate over each pair of names
for i, row1 in df.iterrows():
    for j, row2 in df.iterrows():
        if i < j:
            # get the coordinates of the stadiums
            lat1, lon1 = row1['latitude'], row1['longitude']
            lat2, lon2 = row2['latitude'], row2['longitude']

            # compute the distance between the stadiums using the Haversine formula
            dist = haversine(lat1, lon1, lat2, lon2)

            # update the distance matrix
            dist_matrix.loc[row1['name'], row2['name']] = dist
            dist_matrix.loc[row2['name'], row1['name']] = dist

# save the distance matrix to a CSV file
dist_matrix.to_csv('distance_matrix.csv')
