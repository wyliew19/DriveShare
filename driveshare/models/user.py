from dataclasses import dataclass
from fastapi import Request

@dataclass
class User:
    """Class representing a user in the system"""
    id: int
    """ID of user in database"""
    email: str
    """Email of user"""
    password: str
    """Password of user"""