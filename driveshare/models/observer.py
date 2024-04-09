from abc import ABC, abstractmethod
from enum import Enum
from driveshare.notify import EmailHandler
from driveshare.models.listing import Listing

class MessageType(Enum):
    PURCHASE = 1
    RATING = 2

class AbstractObserver(ABC):
    @abstractmethod
    def update(self, route: MessageType):
        pass

class AbstractSubject(ABC):
    @abstractmethod
    def attach(self, observer: AbstractObserver):
        pass

    @abstractmethod
    def detach(self, observer: AbstractObserver):
        pass

    @abstractmethod
    def notify(self, route: MessageType):
        pass

class Observer(AbstractObserver):
    def __init__(self, email: str, subject: AbstractSubject):
        self.subject = subject
        self.subject.attach(self)
        self.email = email
        self.email_handler = EmailHandler()

    def __eq__(self, other):
        if isinstance(other, str):
            return self.email == other
        return self.email == other.email

    def update(self, route: MessageType, listing: Listing, amount: float | None):
        if route == MessageType.PURCHASE:
            self.email_handler.notify_purchase(self.email, listing, amount)
        elif route == MessageType.RATING:
            self.email_handler.notify_rating(self.email, listing)

