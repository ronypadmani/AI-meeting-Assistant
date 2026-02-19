from pymongo import MongoClient

# Replace with your actual MongoDB connection string
MONGO_URI = "mongodb+srv://rony:Rony3446@cluster0.awfrivu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)

# Select database and collection
db = client["test_db"]
collection = db["test_collection"]

# Insert a sample document
doc_id = collection.insert_one({"name": "User1", "msg": "Hello from Python!"}).inserted_id
print(f"Inserted document with ID: {doc_id}")

# Read documents
for doc in collection.find():
    print(doc)
