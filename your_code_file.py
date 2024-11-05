import random
import string
import json
import os
from dataclasses import dataclass

# Data class for representing a user
@dataclass
class User:
    username: str
    email: str
    id: int

# Function to generate a random username
def generate_username(length=8):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

# Function to generate a list of User objects
def generate_users(count):
    return [User(username=generate_username(), email=f"user{i}@example.com", id=i) for i in range(count)]

# Function to write users to a JSON file
def write_users_to_file(users, filename):
    with open(filename, 'w') as f:
        json.dump([user.__dict__ for user in users], f)

# Function to read users from a JSON file
def read_users_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return [User(**data) for data in json.load(f)]
    return []

# Generator to yield batches of users
def user_batches(users, batch_size):
    for i in range(0, len(users), batch_size):
        yield users[i:i+batch_size]