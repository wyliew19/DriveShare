import sqlite3
from listing import Listing

class DatabaseHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance: 
            cls._instance = super(DatabaseHandler, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__() 
        return cls._instance

    def __init__(self, database_name='driveshare.db'):
        self.database_name = database_name
        self._ensure_db()

    def _ensure_db(self):
        """Ensure the database and listing table exist"""
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT UNIQUE NOT NULL,
                            password TEXT,
                            security_answer1 TEXT,
                            security_answer2 TEXT,
                            security_answer3 TEXT,
                        )''')
        conn.commit()
        cursor.execute('''CREATE TABLE IF NOT EXISTS listings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            seller_id INTEGER,
                            buyer_id INTEGER,
                            make TEXT,
                            model TEXT,
                            year INTEGER,
                            color TEXT,
                            type TEXT,
                            price REAL,
                            location TEXT
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
                raise

    def login(self, email: str, password: str) -> bool:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM users WHERE email = ? AND password = ?''', (email, password))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def securityAnswers(self, secAnswer1: str, secAnswer2: str, secAnswer3: str):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO users (security_answer1, security_answer2, security_answer3)
                              VALUES (?, ?, ?)''', (secAnswer1, secAnswer2, secAnswer3))
            conn.commit()
            print("Successfully registered answers")
        finally:
            conn.close()

    def save_listing(self, listing: Listing):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO listings (seller_id, buyer_id, make, model, year, color, type, price, location)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (listing.seller_id, listing.buyer_id, listing.car.make, listing.car.model, 
                           listing.car.year, listing.car.color, listing.car.type, listing.car.price, listing.car.location))
        conn.commit()
        conn.close()

    def get_listings(self) -> list[tuple]:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM listings WHERE buyer_id IS NULL''')
        listings = cursor.fetchall()
        conn.close()
        return listings
    
    def get_listing(self, listing_id: int) -> tuple:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM listings WHERE id = ?''', (listing_id,))
        listing = cursor.fetchone()
        conn.close()
        return listing