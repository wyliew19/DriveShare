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
        +get_user_email(id: int) str
        ...
        ...()
    }
    namespace security {
    class Hasher {
        +algorithm: str
        +Hasher(algorithm)
        +hash(data: str) str
        +verify(data: str, hashed: str) bool
    }
    }
    DatabaseHandler "1" --> "1" Hasher: hasher
```
We are using a main `DatabaseHandler` class to interface with our SQL database, with mediators handling specific operations.

# Users Handling
```mermaid
classDiagram
    class DatabaseHandler {
        ...
        +register(email: str, password: str) Optional[User]
        +login(email: str, password: str) Optional[User]
        +securityAnswers(id: int, secAnswer1: str, secAnswer2: str, secAnswer3: str)
        +get_security_answers(email: str) tuple[str]
        +add_balance(amount: float)
        +get_balance(email: str)
        +new_password(email: str, password: str)
        +get_user(email: str) Optional[User]
    }
    class UserMediator {
        +db: DatabaseHandler
        +register(email: str, password: str) Optional[User]
        +login(email: str, password: str) Optional[User]
        +securityAnswers(id: int, secAnswer1: str, secAnswer2: str, secAnswer3: str)
        +get_security_answers(email: str) tuple[str]
        +new_password(email: str, password: str)
    }
    class User {
        +id: int
        +email: str
        +balance: float
    }
    DatabaseHandler <-- UserMediator : uses
    DatabaseHandler "1" -- "1" User
    UserMediator "1" -- "1" User
    Server --> UserMediator : uses
```
We use a mediator class between server and accesing user information from the database. This helps to divide the functions of the database's interface nicely. `User` objects are just used for storing the user data.

# Chain of Responsibility
```mermaid
classDiagram
    class DatabaseHandler {
        +get_user_security_answers(email: str)
        +verify_password
    }
    class SecurityQuestionHandler {
        -next_handler: SecurityQuestionHandler
        +db_handler: DatabaseHandler
        +handle(email: str, answer: str, ques_num: int) bool
    }
    class SecurityQuestion1Handler {
        +handle(email: str, answer: str)
    }
    class SecurityQuestion2Handler {
        +handle(email: str, answer: str)
    }
    class SecurityQuestion3Handler {
        +handle(email: str, answer: str)
    }
    SecurityQuestionHandler "1" --> "*" DatabaseHandler: uses
    SecurityQuestionHandler <|-- SecurityQuestion1Handler
    SecurityQuestionHandler <|-- SecurityQuestion2Handler
    SecurityQuestionHandler <|-- SecurityQuestion3Handler
    SecurityQuestion1Handler --> SecurityQuestion2Handler: next_handler
    SecurityQuestion2Handler --> SecurityQuestion3Handler: next_handler
```
The `SecurityQuestionHandler` class is a handler that can handle a request or pass it to the next handler in the chain (`next_handler`). The `SecurityQuestion1Handler`, `SecurityQuestion2Handler`, and `SecurityQuestion3Handler` classes are concrete handlers that handle the request or pass it along. The `DatabaseHandler` class is used by the handlers to get user security answers and verify password

# Listing Handling
```mermaid
classDiagram
    class DatabaseHandler {
        ...
        ...()
        +save_listing()
        +get_listings() list[tuple]
        +get_listing() tuple
        +purchase_listing()
        +get_purchase_history()
        +get_rating()
        +thumbs_up()
        +thumbs_down()
    }
    class ListingMediator {
        +db: DatabaseHandler
        ...
        +ListingMediator[key] : listing
        -tuple_to_listing(listing_tuple) 
        +create_listing(listing.attr)
        +get_listings(Optional[id]: int, Optional[filters]: dict[str,str])
        +get_listing(id: int) Listing
        +get_purchase_history(id: int, Optional[filters] : dict[str,str])
    }
    class ListingBuilder {
        +reset()
        +build_listing(listing.attr)
        +set_id(id: int)
        +set_seller_id(id: int)
        +set_buyer_id(id: int)
        +set_car(make, model, year, color, type, price)
        +set_location(city, state)
        +set_availability(start_date, end_date)
        +get_listing() Listing
    }
    namespace Models {
    class Listing {
        +id: int
        +seller_id: int
        +buyer_id: int
        +car: Car
        +location: Location
        +availability: Availability
    }
    class Car {
        +make: str
        +model: str
        +year: int
        +color: str
        +car_type: str
        +price: float
    }
    class Location {
        +city: str
        +state: str
    }
    class Availability {
        +start_date: str
        +end_date: str
    }
    }
    Listing o-- Car
    Listing o-- Location
    Listing o-- Availability
    ListingBuilder ..> Listing : creates
    ListingMediator --> Listing : uses
    DatabaseHandler --> Listing : uses
    Server --> ListingMediator : uses
```
   
# Observer
```mermaid
classDiagram
    class ListingMediator {
        ...
        +observers: list[AbstractObserver]
        ...()
        +purchase_listing(password: str, listing_id: int, buyer_id: int, days: int)
        +attach(observer: AbstractObserver)
        +detach(observer: AbstractObserver)
        +notify(route: MessageType, email: str, listing: Listing, Optional[amount] : float)
    }
    class MessageType~enum~ {
        +PURCHASE
        +RATING
    }
    class AbstractObserver {
        +update(route: MessageType)
    }
    class AbstractSubject {
        +attach(observer: AbstractObserver)
        +detach(observer: AbstractObserver)
        +notify(route: MessageType)
    }
    class Observer {
        +subject: AbstractSubject
        +email: str
        +email_handler: EmailHandler
        +Observer(email: str, subject: AbstractSubject)
        +update(route: MessageType, listing: Listing, Optional[amount] : float)
    }
    class EmailHandler {
        +send_email(subject: str, body: str, to: str)
    }
    ListingMediator "1" --> "*" AbstractObserver: observers
    AbstractObserver <|-- Observer
    Observer "1" --> "1" AbstractSubject: subject
    Observer "1" --> "1" EmailHandler: email_handler
```
`Obeservers` are notified when a positive rating is recieved or a listing is purchased inside of the `ListingMediator`

# Proxy
```mermaid
classDiagram
    class ListingMediator {
        ...
        ...()
        +purchase_listing(password: str, listing_id: int, buyer_id: int, days: int)
        +rate_listing(listing_id: int, rating: bool)
    }
    class Payment {
        +Payment(email: str)
        +pay(amount: float)
    }
    class PaymentProxy {
        +PaymentProxy(email: str)
        +authorize(password: str, listing: Listing, days: int)
    }
    ListingMediator --> PaymentProxy : asks
    PaymentProxy -- Payment : uses
```
The `ListingMediator` class interacts with the `PaymentProxy` class instead of interacting with the `Payment` class directly. The `PaymentProxy` class controls access to the Payment class, adding a layer of security. The `Payment` class just prints to the server and signifies the start to the payment process.
