from pymongo import MongoClient

# Replace with your Docker container's IP or container name
uri = "mongodb://172.17.0.2:27017/"  # Use o nome do container ou IP, por exemplo: "mongodb://172.17.0.2:27017/"

# Connect to MongoDB
client = MongoClient(uri)

# Select the database
db = client["projet-app"]

# Access the collections
collection_aggregated = db["aggregated_data"]
collection_edges = db["graph_edges"]
collection_hal = db["hal_results_cleaned"]
collection_sankey = db["sankey_data"]
collection_data = db["data"]  # Added the data collection

# Example: fetch the first 5 documents from each collection
print("Aggregated data:")
for doc in collection_aggregated.find().limit(5):
    print(doc)

print("\nGraph edges:")
for doc in collection_edges.find().limit(5):
    print(doc)

print("\nHAL results cleaned:")
for doc in collection_hal.find().limit(5):
    print(doc)

print("\nSankey data:")
for doc in collection_sankey.find().limit(5):
    print(doc)

print("\nData:")
for doc in collection_data.find().limit(5):
    print(doc)
