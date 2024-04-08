import sqlite3
from typing import Optional
from driveshare.models.listing import Listing
from driveshare.models.user import User
from driveshare.security.hash import Hasher

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
        self.hasher = Hasher('sha256')
        self._ensure_db()
        if not self.get_user('johndoe@yahoo.com'):
            self._init_users()
        if not self.get_listings():
            self._dummy_listings()

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
                            start_date TEXT,
                            end_date TEXT
                        )''')
        conn.commit()
        conn.close()

    def _init_users(self):
        self.register('johndoe@yahoo.com', 'password')
        self.register('wyliew@umich.edu', 'password1')
        self.register('leodiaz@umich.edu', 'password2')

    def _dummy_listings(self):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO listings (seller_id, make, model, year, color, type, price, state, city, start_date, end_date)
                          VALUES (1, 'Toyota', 'Corolla', 2020, 'Black', 'Sedan', 50.0, 'California', 'Los Angeles', '2024-04-01', '2024-04-10'),
                                 (1, 'Honda', 'Accord', 2018, 'Red', 'Sedan', 60.0, 'California', 'San Francisco', '2024-04-01', '2024-04-10'),
                                 (2, 'Ford', 'Mustang', 2019, 'Blue', 'Coupe', 70.0, 'Texas', 'Houston', '2024-04-01', '2024-04-10')''')
        conn.commit()
        conn.close()

    def get_user(self, email: str) -> Optional[User]:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE email = ?''', (email,))
        user = cursor.fetchone()
        conn.close()
        if user is None:
            return None
        return User(user[0], user[1])

    def register(self, email: str, password: str) -> Optional[User]:
        password = self.hasher.hash(password)
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO users (email, password) 
                              VALUES (?, ?)''', (email, password))
            conn.commit()
            print("User registered successfully")
            cursor.execute('''SELECT id FROM users WHERE email = ?''', (email,))
            id = cursor.fetchone()[0]
            conn.close()
            return User(id, email)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.email" in str(e):
                return None
            else:
                raise e
            
    def get_security_answers(self, email: str) -> tuple:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT security_answer1, security_answer2, security_answer3 FROM users WHERE email = ?''', (email,))
        answers = cursor.fetchone()
        conn.close()
        return answers
    
    def new_password(self, email: str, password: str):
        password = self.hasher.hash(password)
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''UPDATE users SET password = ? WHERE email = ?''', (password, email))
        conn.commit()
        conn.close()

    def login(self, email: str, password: str) -> Optional[User]:
        password = self.hasher.hash(password)
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT id FROM users WHERE email = ? AND password = ?''', (email, password))
        id = cursor.fetchone()
        conn.close()
        if id:
            return User(id[0], email)
        return None
    
    def securityAnswers(self, id: int, secAnswer1: str, secAnswer2: str, secAnswer3: str):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''UPDATE users SET security_answer1 = ?, 
                              security_answer2 = ?, 
                              security_answer3 = ? WHERE id = ?''',
                              (secAnswer1, secAnswer2, secAnswer3, id))
            conn.commit()
            print("Successfully registered answers")
        finally:
            conn.close()

    def save_listing(self, listing: Listing):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO listings (seller_id, buyer_id, make, model, year, color, type, price, state, city, start_date, end_date)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (listing.seller_id, listing.buyer_id, listing.car.make, listing.car.model, 
                           listing.car.year, listing.car.color, listing.car.type, listing.car.price,
                           listing.location.state, listing.location.city, listing.availability.start_date,
                           listing.availability.end_date))
        conn.commit()
        conn.close()

    def get_listings(self, id: int | None = None, filters: dict[str, str] | None = None) -> Optional[list[tuple]]:
        """Get listings from the database   
        Args:
            id (int, optional): The ID of the seller. Defaults to None.
            filters (dict[str, str], optional): Filters to apply to the listings. Defaults to None."""
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM listings''')
        if not cursor.fetchall():
            return None
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

        if not params and id is None:
            query += 'ERE buyer_id IS NULL'

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

    def get_purchase_history(self, id: int) -> list[tuple]:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM listings WHERE buyer_id = ?''', (id,))
        listings = cursor.fetchall()
        conn.close()
        return listings
    
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

    def get_user_security_answers(self, email: str) -> tuple:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT security_answer1, security_answer2, security_answer3 FROM users WHERE email = ?''', (email,))
        answers = cursor.fetchone()
        conn.close()
        return answers