from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")

# Database
db = client["student_management_db"]

# Collection
students_collection = db["students"]
