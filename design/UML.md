```mermaid
classDiagram
    class User {
        +register(email: str, password: str)
        +login(email: str, password: str)
        +viewRentalHistory()
        +answerSecurityQuestion(question: str, answer: str)
    }
    class Car {
        +listCar(details: CarDetails)
        +updateAvailability()
        +updatePrice()
    }
    class Booking {
        +searchCars(location: str, date: Date)
        +bookCar(car: Car, period: Period)
    }
    class Message {
        +sendMessage(to: User, content: str)
        +receiveMessage(from: User, content: str)
    }
    class Payment {
        +makePayment(amount: Float)
    }
    class Review {
        +leaveReview(content: str, rating: Int)
    }
    User "1" -- "*" Car : owns
    User "1" -- "*" Booking : makes
    User "1" -- "*" Message : sends/receives
    User "1" -- "*" Payment : makes
    User "1" -- "*" Review : leaves
    Car "1" -- "*" Booking : is booked in
    Booking "1" -- "*" Message : triggers
    Booking "1" -- "*" Payment : triggers
    Booking "1" -- "*" Review : triggers
```
User is singleton with records entered to db through `register()`: ensure 
only a single instance of User with that email and password is available at
a time. Given the user has logged in, set a flag in db stating they have logged in.

TODO: revise this to be more accurate to system (I prefer coding to planning)