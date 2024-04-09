from dataclasses import dataclass

@dataclass
class User:
    """Class representing a user in the system"""
    id: int
    """ID of user in database"""
    email: str
    """Email of user"""
    balance: float
    """Balance of user"""