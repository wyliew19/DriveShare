import sqlite3

class User:
    def __init__(self, database_name='users.db'):
        self.database_name = database_name
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            email TEXT PRIMARY KEY,
                            password TEXT,
                            rental_history TEXT,
                            security_question TEXT,
                            security_answer TEXT
                        )''')
        conn.commit()
        conn.close()

    def register(self, email: str, password: str):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO users (email, password) 
                              VALUES (?, ?)''', (email, password))
            conn.commit()
            print("User registered successfully")
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.email" in str(e):
                raise ValueError("Email already exists, please choose a different one")
            else:
                raise  # Re-raise the exception if it's not due to unique constraint violation
        finally:
            conn.close()

    # Other methods...

