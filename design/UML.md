# Database Handler
```mermaid
classDiagram
    class DatabaseHandler {
        -hasher: Hasher
        -instance: DatabaseHandler
        -DatabaseHandler()
        -ensure_db()
        -init_users()
        -dummy_listings()
        +__new__()
        +register(email: str, password: str) Optional[User]
        +login(email: str, password: str) Optional[User]
        +get_user(email: str) Optional[User]
        +get_user_email(id: int) str
        +securityAnswers(id: int, secAnswer1: str, secAnswer2: str, secAnswer3: str)
        +get_security_answers(email: str) tuple[str]
        +add_balance(amount: float)
        +new_password(email: str, password: str)

    }
    class Hasher {

    }
```
We are using a main DatabaseHandler class to interface with our SQL database, with mediators handling specific operations.

# Users Handling
```mermaid
classDiagram
    class UserMediator {
        +db: DatabaseHandler
        +register(email: str, password: str) Optional[User]
        +login(email: str, password: str) Optional[User]
        +securityAnswers(id: int, secAnswer1: str, secAnswer2: str, secAnswer3: str)
        +get_security_answers(email: str)
        +new_password(email: str, password: str)
    }
    class User {
        +id: int
        +email: str
        +balance: float
    }
    
    SecurityQuestionHandler {

    }
    SecurityQuestion1Handler {

    }
    SecurityQuestion2Handler {
        
    }
    SecurityQuestion3Handler {
        
    }

```
   
# Listing Handling
```mermaid
classDiagram
    class DatabaseHandler {

    }
    class ListingMediator {
        
    }
    class ListingBuilder {

    }
    class Listing {

    }
    class Car {

    }
    class Location {

    }
    class Availability {

    }
```
   
# Observer
```mermaid
classDiagram
    class MessageType {
        +INFO: Enum
        +WARNING: Enum
        +ERROR: Enum
    }
    class AbstractObserver {
        +update(messageType: MessageType, message: str)
    }
    class AbstractSubject {
        +attach(observer: AbstractObserver)
        +detach(observer: AbstractObserver)
        +notify()
    }
    class Observer {
        +update(messageType: MessageType, message: str)
    }
    class EmailHandler {
        +send_email(subject: str, body: str, to: str)
    }
```

# Proxy
```mermaid
classDiagram
    Payment {

    }
    PaymentProxy {

    }