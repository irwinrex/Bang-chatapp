# chat/mongo.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import environ
import os
import datetime
import logging
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Set up logging
logger = logging.getLogger(__name__)

# Establish MongoDB connection
MONGO_URI = env('MONGO_URI')  # Make sure to set this in your .env file

client = MongoClient(MONGO_URI)

# Check if the connection is successful
try:
    client.admin.command('ping')  # Check connection
    logger.info("MongoDB connection successful")
except ConnectionFailure:
    logger.error("MongoDB connection failed")
    raise

# Select the database and collection
db = client['your_database_name']  # Replace with your actual database name
chat_messages_collection = db['chat_messages']  # Collection name for chat messages

def save_chat_message(room_name, sender, message):
    """Save a chat message to MongoDB."""
    chat_message = {
        "room_name": room_name,
        "sender": sender,
        "message": message,
        "timestamp": datetime.datetime.now()  # Add timestamp
    }

    try:
        chat_messages_collection.insert_one(chat_message)
        logger.info(f"Message saved to MongoDB: {chat_message}")
    except PyMongoError as e:
        logger.error(f"Error saving message to MongoDB: {e}")
