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
        if not self.get_user('admin@driveshare.com'):
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
                            security_answer3 TEXT,
                            balance DECIMAL(10, 2) DEFAULT 0.0,
                            thumbs_up INTEGER DEFAULT 0,
                            thumbs_down INTEGER DEFAULT 0
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
                            end_date TEXT,
                            FOREIGN KEY (seller_id) REFERENCES users(id),
                            FOREIGN KEY (buyer_id) REFERENCES users(id)
                        )''')
        conn.commit()
        conn.close()

    def _init_users(self):
        self.register('admin@driveshare.com', 'admin')
        for i in range(1, 10):
            self.register(f'user{i}@driveshare.com', f'password{i}')
            self.securityAnswers(i+1, 'answer1', 'answer2', 'answer3')

    def _dummy_listings(self):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO listings (seller_id, make, model, year, color, type, price, state, city, start_date, end_date)
                     VALUES (1, 'Toyota', 'Corolla', 2020, 'Black', 'Sedan', 50.0, 'Michigan', 'Detroit', '2024-04-01', '2024-04-10'),
                            (1, 'Honda', 'Accord', 2018, 'Red', 'Sedan', 60.0, 'Michigan', 'Utica', '2024-04-05', '2024-04-15'),
                            (2, 'Ford', 'Mustang', 2019, 'Blue', 'Coupe', 70.0, 'Michigan', 'Dearborn', '2024-04-10', '2024-04-20'),
                            (4, 'BMW', '3 Series', 2019, 'White', 'Sedan', 90.0, 'Michigan', 'Lansing', '2024-04-15', '2024-04-25'),
                            (5, 'Audi', 'A4', 2020, 'Black', 'Sedan', 100.0, 'Michigan', 'Flint', '2024-04-20', '2024-04-30'),
                            (6, 'Mercedes', 'C Class', 2021, 'Silver', 'Sedan', 110.0, 'Michigan', 'Grand Rapids', '2024-04-25', '2024-05-05'),
                            (7, 'Tesla', 'Model 3', 2022, 'Red', 'Sedan', 120.0, 'Michigan', 'Kalamazoo', '2024-05-01', '2024-05-11'),
                            (8, 'Subaru', 'Impreza', 2019, 'Gray', 'Sedan', 80.0, 'Michigan', 'Warren', '2024-05-05', '2024-05-15'),
                            (9, 'Jeep', 'Wrangler', 2021, 'Black', 'SUV', 85.0, 'Michigan', 'Detroit', '2024-05-10', '2024-05-20'),
                            (10, 'Ford', 'F-150', 2020, 'Red', 'Truck', 90.0, 'Michigan', 'Utica', '2024-05-15', '2024-05-25'),
                            (4, 'Chevrolet', 'Silverado', 2019, 'Blue', 'Truck', 95.0, 'Michigan', 'Dearborn', '2024-05-20', '2024-05-30'),
                            (6, 'Toyota', '4Runner', 2022, 'White', 'SUV', 100.0, 'Michigan', 'Ann Arbor', '2024-05-25', '2024-06-05'),
                            (5, 'BMW', 'Z4', 2021, 'Black', 'Convertible', 105.0, 'Michigan', 'Lansing', '2024-06-01', '2024-06-11')''')
        conn.commit()
        conn.close()

    def get_user(self, email: str) -> Optional[User]:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT id, email, balance FROM users WHERE email = ?''', (email,))
        user = cursor.fetchone()
        conn.close()
        if user is None:
            return None
        return User(user[0], user[1], user[2])

    def get_user_email(self, id: int) -> str:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT email FROM users WHERE id = ?''', (id,))
        email = cursor.fetchone()[0]
        conn.close()
        return email

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
            return User(id, email, 0)
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

    def add_balance(self, email: str, amount: float):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''UPDATE users SET balance = balance + ? WHERE email = ?''', (amount, email))
        conn.commit()
        conn.close()
    
    def new_password(self, email: str, password: str):
        password = self.hasher.hash(password)
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''UPDATE users SET password = ? WHERE email = ?''', (password, email))
        conn.commit()
        conn.close()

    def login(self, email: str, password: str) -> Optional[User]:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT id, password, balance FROM users WHERE email = ?''', (email,))
        tup = cursor.fetchone()
        conn.close()
        if tup and self.hasher.verify(password, tup[1]):
            return User(tup[0], email, tup[1])
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
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (listing.seller_id, listing.buyer_id, listing.car.make, listing.car.model, 
                           listing.car.year, listing.car.color, listing.car.car_type, listing.car.price,
                           listing.location.state, listing.location.city, listing.availability.start_date,
                           listing.availability.end_date))
        conn.commit()
        conn.close()

    def get_listings(self, id: int | None = None, filters: dict[str, str] | None = None, is_buyer: bool | None = False) -> Optional[list[tuple]]:
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
            if is_buyer:
                query += 'buyer_id = ? AND '
            else:
                query += 'seller_id = ? AND '
            params.append(id)

        if filters is not None:
            filter_queries = {'make': 'make = ?', 'model': 'model = ?', 'year': 'year = ?',
                              'color': 'color = ?', 'type': 'type = ?', 'price': 'price <= ?',
                              'state': 'state = ?', 'city': 'city LIKE ?', 'start_date': 'start_date >= ?',
                              'end_date': 'end_date <= ?'}
            for key, value in filters.items():
                if value is None:
                    continue
                query += filter_queries[key] + ' AND '
                params.append(value)

        # Remove the last ' AND ' from the query
        query = query[:-4]

        if not params and id is None:
            query += 'ERE buyer_id IS NULL'

        cursor.execute(query, tuple(params))
        listings = cursor.fetchall()
        conn.close()
        return listings

    def thumbs_up(self, id: int):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''UPDATE users SET thumbs_up = thumbs_up + 1 WHERE id = ?''', (id,))
        conn.commit()
        conn.close()

    def thumbs_down(self, id: int):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''UPDATE users SET thumbs_down = thumbs_down + 1 WHERE id = ?''', (id,))
        conn.commit()
        conn.close()

    def get_rating(self, id: int) -> tuple:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT thumbs_up, thumbs_down FROM users WHERE id = ?''', (id,))
        rating = cursor.fetchone()
        conn.close()
        return rating
    
    def get_listing(self, listing_id: int) -> tuple:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM listings WHERE id = ?''', (listing_id,))
        listing = cursor.fetchone()
        conn.close()
        return listing

    def get_purchase_history(self, id: int, filters: dict[str, str]) -> Optional[list[tuple]]:
        listings = self.get_listings(id=id, filters=filters, is_buyer=True)
        return listings
    
    def purchase_listing(self, listing_id: int, email: str, days: int) -> bool:
        buyer_id = self.get_user(email).id
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''UPDATE listings SET buyer_id = ? WHERE id = ?''', (buyer_id, listing_id))
        conn.commit()
        cursor.execute('''SELECT balance FROM users WHERE email = ?''', (email,))
        balance = cursor.fetchone()[0]
        cursor.execute('''SELECT price FROM listings WHERE id = ?''', (listing_id,))
        price = cursor.fetchone()[0]
        if balance < price * days:
            return False
        try:
            cursor.execute('''UPDATE users SET balance = balance - ? WHERE email = ?''', (price * days, email))
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            conn.close()
        return True

    def get_balance(self, email: str) -> float:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT balance FROM users WHERE email = ?''', (email,))
        balance = cursor.fetchone()[0]
        conn.close()
        return balance

    def get_user_security_answers(self, email: str) -> tuple:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT security_answer1, security_answer2, security_answer3 FROM users WHERE email = ?''', (email,))
        answers = cursor.fetchone()
        conn.close()
        return answers

    def verify_password(self, email: str, password: str) -> bool:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT password FROM users WHERE email = ?''', (email,))
        correct_password = cursor.fetchone()[0]
        conn.close()
        return self.hasher.verify(password, correct_password)
    