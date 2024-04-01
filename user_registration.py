import sqlite3

class User:
    #This line defines a class-level variable _instance and initializes it to None. 
    #This variable will be used to store the single instance of the class.
    _instance = None

    '''This is a special method in Python called __new__. 
    It is a static method that is called to create a new instance of the class. 
    It is responsible for creating and returning a new object of the class.'''
    def __new__(cls, *args, **kwargs):
        if not cls._instance: 
            '''If no instance of the class exists (_instance is None), 
            this line creates a new instance of the class by calling the __new__ method of 
            the superclass (super(User, cls).__new__) and passing 
            the class (cls), along with any arguments and keyword arguments (*args and **kwargs).'''
            cls._instance = super(User, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__() #This creates a new instance
        return cls._instance #This returns the single instance of the class
    '''In summary, this code implements the Singleton pattern by ensuring that only one instance 
    of the User class is created throughout the application. The __new__ method 
    is overridden to control the creation of instances, and the _instance variable is 
    used to store and return the single instance of the class.'''
    
    '''If someone tries to create another instance of User, 
    the __new__ method will be called again. However, this time, 
    cls._instance will not be None because it was set to the 
    first instance created earlier. Therefore, the code inside the 
    if not cls._instance will not be executed. Instead, the 
    existing instance stored in cls._instance will be returned directly.'''

    def __init__(self, database_name='users.db'):
        self.database_name = database_name

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

    def login(self, email: str, password: str) -> bool:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM users WHERE email = ? AND password = ?''', (email, password))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    # Other methods...

