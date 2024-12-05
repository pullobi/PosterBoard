import os
import sqlite3
import hashlib

# Paths for database
DB_DIR = "./database"
DB = os.path.join(DB_DIR, "manager.db")


def initialize_database():
    """Create database and users table if they don't exist."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    
    # Create the users table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        hashed_pwd TEXT NOT NULL
    )
    """)
    
    connection.commit()
    connection.close()
    print(f"Database initialized at {DB}")

def sha256_hash(input_data: str) -> str:
    """Hashes input_data using SHA-256 and returns the hexadecimal digest."""
    input_bytes = input_data.encode('utf-8')
    sha256 = hashlib.sha256()
    sha256.update(input_bytes)
    return sha256.hexdigest()

def newUser(username: str, password: str):
    """Creates a new user with the specified username and hashed password."""
    hashed_password = sha256_hash(password)

    try:
        connection = sqlite3.connect(DB)
        cursor = connection.cursor()
        
        # Insert user into the database
        cursor.execute("""
        INSERT INTO users (username, hashed_pwd) 
        VALUES (?, ?)
        """, (username, hashed_password))
        
        connection.commit()
        print(f"User '{username}' added successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
    finally:
        connection.close()

def checkUser(username: str, password: str) -> bool:
    """Checks credentials by comparing the hashed password with the one in the database."""
    hashed_password = sha256_hash(password)

    try:
        connection = sqlite3.connect(DB)
        cursor = connection.cursor()

        # Query for the hashed password of the given username
        cursor.execute("""
        SELECT hashed_pwd FROM users WHERE username = ?
        """, (username,))
        result = cursor.fetchone()

        # If the username exists, compare the password hash
        if result and result[0] == hashed_password:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error during user authentication: {e}")
        return False
    finally:
        connection.close()

def deleteUser(username: str):
    """Deletes a user from the database by username."""
    try:
        connection = sqlite3.connect(DB)
        cursor = connection.cursor()
        
        cursor.execute("""
        DELETE FROM users WHERE username = ?
        """, (username,))
        
        connection.commit()
        print(f"User '{username}' deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting user '{username}': {e}")
    finally:
        connection.close()

def listUsers() -> list:
    """Returns a list of all users with their usernames and IDs from the database."""
    try:
        connection = sqlite3.connect(DB)
        cursor = connection.cursor()
        
        cursor.execute("""
        SELECT id, username FROM users
        """)
        
        result = cursor.fetchall()
        users = [{"id": row[0], "username": row[1]} for row in result]
        
        return users
    except sqlite3.Error as e:
        print(f"Error listing users: {e}")
        return []
    finally:
        connection.close()