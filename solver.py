import pandas as pd
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Load the teams and venues data
teams = pd.read_csv(
    'data/teams.csv')
venues = pd.read_csv(
    'data/venues.csv')

# Load the airports data
airports = pd.read_csv(
    'data/airports.csv')

# Load the travel time data
bus_travel_data = pd.read_csv(
    'data/bus_travel_data.csv')
print(teams['name'])
air_travel_data = pd.read_csv(
    'data/air_travel_data.csv')
print(teams['name'])

# Calculate the travel times
bus_travel_times = pd.DataFrame(
    np.zeros((len(teams), len(teams))),
    columns=teams.name,
    index=teams.name
)

air_travel_times = pd.DataFrame(
    np.zeros((len(teams), len(teams))),
    columns=teams.name,
    index=teams.name
)

for i, from_team in teams.iterrows():
    for j, to_team in teams.iterrows():
        if i != j:
            travel_time = None
            if from_team['city'] == to_team['city']:
                travel_time = bus_travel_data.loc[from_team['name'], to_team['name']]
            else:
                travel_data = air_travel_data[(air_travel_data['Origin'] == from_team['city']) & (
                    air_travel_data['Destination'] == to_team['city'])]
                if len(travel_data) > 0:
                    travel_time = travel_data.iloc[0]['Travel Time (hrs)']
            if travel_time is not None:
                bus_travel_times.iloc[i, j] = travel_time
                air_travel_times.iloc[i, j] = travel_time

# Add the coordinates to the venues and airports data
venues['lat_long'] = list(zip(venues.latitude, venues.longitude))
airports['lat_long'] = list(zip(airports.latitude, airports.longitude))

# Create a distance matrix from the venues and airports data
distance_matrix = pd.DataFrame(
    np.zeros((len(venues), len(venues))), columns=venues.name, index=venues.name)

for i in range(len(venues)):
    for j in range(i, len(venues)):
        venue_distance = np.linalg.norm(
            np.array(venues.iloc[i]['lat_long']) - np.array(venues.iloc[j]['lat_long']))
        if venue_distance <= 200:
            distance_matrix.iloc[i, j] = venue_distance
            distance_matrix.iloc[j, i] = venue_distance

            for k in range(len(airports)):
                airport_distance_1 = np.linalg.norm(
                    np.array(venues.iloc[i]['lat_long']) - np.array(airports.iloc[k]['lat_long']))
                airport_distance_2 = np.linalg.norm(
                    np.array(venues.iloc[j]['lat_long']) - np.array(airports.iloc[k]['lat_long']))
                if airport_distance_1 <= 200 and airport_distance_2 <= 200:
                    distance_matrix.iloc[i,
                                         j] = airport_distance_1 + airport_distance_2
                    distance_matrix.iloc[j,
                                         i] = airport_distance_1 + airport_distance_2


def get_closest_airports(from_venue, to_venue, airports):
    from_airports = airports.copy()
    to_airports = airports.copy()
    from_airports['distance'] = from_airports['lat_long'].apply(
        lambda x: np.linalg.norm(np.array(x) - np.array(from_venue['lat_long'])))
    to_airports['distance'] = to_airports['lat_long'].apply(
        lambda x: np.linalg.norm(np.array(x) - np.array(to_venue['lat_long'])))
    closest_from_airport = from_airports.loc[from_airports['distance'].idxmin(
    )]
    closest_to_airport = to_airports.loc[to_airports['distance'].idxmin()]
    airport_distance = np.linalg.norm(
        np.array(closest_from_airport['lat_long']) - np.array(closest_to_airport['lat_long']))
    return closest_from_airport, closest_to_airport, airport_distance


# Define the time window constraints
def create_time_callback(time_matrix):
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        travel_time = time_matrix[from_node][to_node]
        if travel_time == 0:
            return 0
        from_team = teams.loc[from_node]
        to_team = teams.loc[to_node]
        from_arrival_time = max(time_callback(
            from_index-1, from_index), from_team['start_time']) + 1
        if to_team['week'] == 33:
            to_arrival_time = 365
        else:
            to_arrival_time = max(time_callback(
                from_index, to_index-1), from_arrival_time + travel_time)
        return to_arrival_time

    return time_callback


# Define the search parameters
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
search_parameters.time_limit.seconds = 30
search_parameters.log_search = True

# Create the routing model
manager = pywrapcp.RoutingIndexManager(len(teams), 2 * len(teams), 0)
routing = pywrapcp.RoutingModel(manager)

# Define the time window constraints
bus_travel_times = bus_travel_times.where(bus_travel_times <= 3, other=3)
air_travel_times = air_travel_times.where(air_travel_times <= 3, other=3)

time_matrix = []
for i in range(len(teams) * 2):
    row = []
    for j in range(len(teams) * 2):
        if i == j:
            row.append(0)
        elif i < len(teams) and j < len(teams):
            row.append(bus_travel_times.iloc[i, j])
        elif i >= len(teams) and j >= len(teams):
            row.append(air_travel_times.iloc[i - len(teams), j - len(teams)])
        else:
            row.append(0)
    time_matrix.append(row)

time_callback_index = routing.RegisterTransitCallback(
    create_time_callback(time_matrix))

print(dir(time_callback_index))

#routing.AddDimensionWithVehicleTransits(time_callback_index,
#    0,  # allow waiting time
#    [365],  # maximum time per vehicle
#    True,  # start cumul to zero
#    'Time')
