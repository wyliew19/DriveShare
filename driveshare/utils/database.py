import sqlite3
from typing import Optional
from driveshare.models.listing import Listing
from driveshare.models.user import User

class DatabaseHandler:
    """A singleton class to handle database operations"""
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
        """Ensure the database and tables exist"""
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT UNIQUE NOT NULL,
                            password TEXT,
                            security_answer1 TEXT,
                            security_answer2 TEXT,
                            security_answer3 TEXT
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
                            city TEXT,
                            state TEXT,
                            availability TEXT
                        )''')
        conn.commit()
        conn.close()

    def get_id(self, email: str) -> int:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT id FROM users WHERE email = ?''', (email,))
        id = cursor.fetchone()[0]
        conn.close()
        return id

    def register(self, email: str, password: str) -> User:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO users (email, password) 
                              VALUES (?, ?)''', (email, password))
            conn.commit()
            print("User registered successfully")
            cursor.execute('''SELECT id FROM users WHERE email = ?''', (email,))
            return User(cursor.fetchone()[0], email, password)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.email" in str(e):
                raise ValueError("Email already exists, please choose a different one")
            else:
                raise

    def login(self, email: str, password: str) -> Optional[User]:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT id FROM users WHERE email = ? AND password = ?''', (email, password))
        id = cursor.fetchone()[0]
        conn.close()
        if id:
            return User(id, email, password)
        return None
    
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
        cursor.execute('''INSERT INTO listings (seller_id, buyer_id, make, model, year, color, type, price, state, city, availability)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (listing.seller_id, listing.buyer_id, listing.car.make, listing.car.model, 
                           listing.car.year, listing.car.color, listing.car.type, listing.car.price,
                           listing.location.state, listing.location.city, listing.availability.days))
        conn.commit()
        conn.close()

    def get_listings(self, id: int | None = None, filters: dict[str, str] | None = None) -> list[tuple]:
        """Get listings from the database   
        Args:
            id (int, optional): The ID of the seller. Defaults to None.
            filters (dict[str, str], optional): Filters to apply to the listings. Defaults to None."""
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        query = 'SELECT * FROM listings WHERE '
        params = []

        if id is not None:
            query += 'seller_id = ? AND '
            params.append(id)

        if filters is not None:
            for key, value in filters.items():
                query += f'{key} = ? AND '
                params.append(value)

        # Remove the last ' AND ' from the query
        query = query[:-4]

        if not params:
            query += 'buyer_id IS NULL'

        cursor.execute(query, tuple(params))
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
    
    def purchase_listing(self, listing_id: int, email: str):
        buyer_id = self.get_id(email)
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''UPDATE listings SET buyer_id = ? WHERE id = ?''', (buyer_id, listing_id))
        conn.commit()
        conn.close()

    def get_user_password(self, email: str) -> str:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT password FROM users WHERE email = ?''', (email,))
        password = cursor.fetchone()[0]
        conn.close()
        return password