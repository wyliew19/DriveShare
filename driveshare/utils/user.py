from typing import Optional
from driveshare.utils.database import DatabaseHandler
from driveshare.models.user import User

class UserMediator:
    """A singleton class for handling user registration and login"""
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
            cls._instance = super(UserMediator, cls).__new__(cls, *args, **kwargs)
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

    def __init__(self):
        self.db = DatabaseHandler()

    def __getitem__(self, key: str | int) -> Optional[User]:
        if isinstance(key, str):
            return self.db.get_user(key)
        return self.db.get_user(self.db.get_user_email(key))

    def register(self, email: str, password: str) -> Optional[User]:
        return self.db.register(email, password)

    def login(self, email: str, password: str) -> Optional[User]:
        return self.db.login(email, password)
    
    def get_balance(self, email: str) -> float:
        return self.db.get_balance(email)

    def add_balance(self, email: str, amount: float):
        self.db.add_balance(email, amount)

    def securityAnswers(self, id: int, secAnswer1: str, secAnswer2: str, secAnswer3: str):
        self.db.securityAnswers(id, secAnswer1, secAnswer2, secAnswer3)

    def get_security_answers(self, email: str):
        return self.db.get_security_answers(email)
    
    def new_password(self, email: str, password: str):
        self.db.new_password(email, password)