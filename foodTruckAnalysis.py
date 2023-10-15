# Commands to install required libraries
# !pip install googlemaps
# !pip install folium

import folium
import googlemaps
import json
from openpyxl import Workbook

# Using GoogleMaps API
api_key = '<MY PERSONAL API KEY>'
gmaps = googlemaps.Client(key=api_key)

# Define the state of Indiana as a bounding box
indiana_bbox = "39.771484,-86.087700|40.761368,-85.806425"

# Search for food trucks in Indiana
food_trucks = gmaps.places(query="food truck", location=indiana_bbox)

# Extract relevant information and print the results
# Fetching required details such as Name, Address, Rating, Website, Open and Close Hours, Latitude, Longitude
food_trucks_results = []
food_trucks_results.append(["Name", "Address", "Rating", "Website", "Open Hours", "Latitude", "Longitude"])
for place in food_trucks["results"]:
    place_id = place["place_id"]
    name = place["name"]
    address = place.get("vicinity", "Address not available")
    rating = place.get("rating", "No rating available")
    website = place.get("website", "Website not available")
    open_hours = place.get("opening_hours", {}).get("weekday_text", "Hours not available")
    cuisine_type = ", ".join(place.get("types", []))
    query = name
    geocode_result = gmaps.geocode(query)
    if geocode_result:
        address = geocode_result[0]["formatted_address"]
    place_details = gmaps.place(place_id=place_id)
    website = place_details["result"].get("website", "Website not available")
    open_hours = place_details["result"].get("opening_hours", "Hours not available")
    if "weekday_text" in open_hours:
        open_hours = open_hours.get("weekday_text", "Hours not available")
    address = place_details["result"].get("formatted_address", "Address not available")
    location = place["geometry"]["location"]
    latitude = location["lat"]
    longitude = location["lng"]
    food_trucks_results.append([name, address, rating, website, open_hours, latitude, longitude])

# Create a new Excel workbook
workbook = Workbook()

# Select the active worksheet (the first sheet by default)
worksheet = workbook.active

data = food_trucks_results
for row in data:
    row[4] = str(row[4])
    worksheet.append(row)

# Save the Excel file with your desired file name
workbook.save('Food_Truck_Analysis.xlsx')

# Fetching Data for Travel Plan
# Fetching the Start Latitude and Start Longitude
startLat = food_trucks_results[1][5]
startLon = food_trucks_results[1][6]

# Create a map centered on your starting location
m = folium.Map(location=[startLat, startLon], zoom_start=12)

# Creating tuples of latitudes and longitudes
locations = []
for each in food_trucks_results[2:]:
    temp = {}
    temp["name"] = each[0]
    temp["address"] = [each[5], each[6] ]
    locations.append(temp)


for location in locations:
    folium.Marker(
        location=location["address"],
        popup=location["name"]
    ).add_to(m)

# Save the map to an HTML file
m.save('Plan_Map.html')

locations = []
for each in food_trucks_results[1:]:
    locations.append((each[5], each[6]))


# Initialize variables to store results
distances = []
durations = []
modes_of_transport = []

# Iterate through the locations and get directions between them
for i in range(len(locations) - 1):
    origin = locations[i]
    destination = locations[i + 1]

    # Perform the Directions API query
    directions = gmaps.directions(
        origin=origin,
        destination=destination,
        mode="driving",  # You can change the mode of transport here (e.g., "walking", "transit")
    )

    # Extract and print the distance, duration, and mode of transport
    route = directions[0]["legs"][0]
    distance = route["distance"]["text"]
    duration = route["duration"]["text"]
    mode = route["steps"][0]["travel_mode"]

    distances.append(distance)
    durations.append(duration)
    modes_of_transport.append(mode)

# Compiling the distances, durations and modes of transport
# Create a new Excel workbook
workbook = Workbook()

# Select the active worksheet (the first sheet by default)
worksheet = workbook.active

# data = food_trucks_results
worksheet.append(["From Location", "To Location", "Distance", "Duration", "Mode of Transport"])
for i in range(len(locations) - 1):
    from_loc = food_trucks_results[i + 1][0]
    to_loc = food_trucks_results[i + 2][0]
    distance = distances[i]
    duration = durations[i]
    mode = modes_of_transport[i]
    worksheet.append([from_loc, to_loc, distance, duration, mode])

# Save the Excel file with your desired file name
workbook.save('Travel_Plan.xlsx')