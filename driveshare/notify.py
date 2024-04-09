import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from driveshare.utils.listing import Listing

class EmailHandler:
    EMAIL = "driveshare.emailer@gmail.com"

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmailHandler, cls).__new__(cls)
        return cls._instance

    def notify_purchase(self, email: str, listing: Listing, amount: float):
        
        # Code to send email to seller
        subject = "Car Rental Confirmation"
        message = f"""Congratulations! Your car, {listing.car.make} {listing.car.model}, has been successfully rented.
        A sum of ${amount:.2f} has been transferred to your account."""

        msg = MIMEMultipart()
        msg["From"] = EmailHandler.EMAIL
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EmailHandler.EMAIL, "xhwp dvkt qkoo bmhb")
            server.send_message(msg)
        
    def notify_rating(self, email: str, listing: Listing):
        
        # Code to send email to seller
        subject = "Car Rental Rating"
        message = f"""Your car, {listing.car.make} {listing.car.model}, has been rated given a thumbs up by a recent renter."""

        msg = MIMEMultipart()
        msg["From"] = EmailHandler.EMAIL
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EmailHandler.EMAIL, "xhwp dvkt qkoo bmhb")
            server.send_message(msg)
