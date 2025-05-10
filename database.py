import sqlite3
from email_validator import validate_email, EmailNotValidError

def is_valid_email(email: str) -> bool:
    """ Validate the email using the email-validator package """
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def connect_db():
    """ Connect to SQLite database (it will create it if it doesn't exist) """
    conn = sqlite3.connect("users.db")
    return conn

def create_user_table():
    """ Create the users table if it doesn't already exist """
    conn = connect_db()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            weight REAL,
            height REAL,
            goal TEXT,
            experience TEXT,
            diet TEXT
        )
    ''')

    conn.commit()
    conn.close()

def add_user(email, name, password):
    """ Add a new user to the database """
    if not is_valid_email(email):  # Check email validity before adding user
        print(f"Invalid email: {email}")
        return None
    
    conn = connect_db()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)", (email, name, password))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Email {email} already exists in the database.")
        return None
    finally:
        conn.close()

def authenticate_user(email, password):
    """ Authenticate user using email and password """
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    result = c.fetchone()
    conn.close()
    return result

def get_user(email):
    """ Fetch user profile by email """
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    result = c.fetchone()
    conn.close()
    return result

def update_profile(email, age, gender, weight, height, goal, experience, diet):
    """ Update the user's profile with fitness details """
    conn = connect_db()
    c = conn.cursor()
    
    c.execute('''UPDATE users SET age=?, gender=?, weight=?, height=?, goal=?, experience=?, diet=? 
                 WHERE email=?''', 
              (age, gender, weight, height, goal, experience, diet, email))
    conn.commit()
    conn.close()

def get_user_profile(email):
    """ Fetch and return the complete profile of a user given their email """
    user = get_user(email)
    if user:
        profile = {
            "name": user[1],
            "email": user[2],
            "age": user[4],
            "gender": user[5],
            "weight": user[6],
            "height": user[7],
            "goal": user[8],
            "experience": user[9],
            "diet": user[10]
        }
        return profile
    return None

# Call this once to create the table when the script is first run
create_user_table()
