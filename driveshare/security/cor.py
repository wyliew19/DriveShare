from typing import Optional
from driveshare.utils.database import DatabaseHandler

class SecurityQuestionHandler:
    def __init__(self, next_handler: Optional['SecurityQuestionHandler'] = None):
        self._next_handler = next_handler
        self.db_handler = DatabaseHandler()

    def handle(self, email: str, answer: str, question_number: int) -> bool:
        answers = self.db_handler.get_security_answers(email)
        if answers is None:
            return False
        correct_answer = self.db_handler.get_security_answers(email)[question_number]
        if answer != correct_answer:
            return False
        if self._next_handler is not None:
            return self._next_handler.handle(email, answer, question_number)
        return True

class SecurityQuestion1Handler(SecurityQuestionHandler):
    def handle(self, email: str, answer: str) -> bool:
        return super().handle(email, answer, 0)
    
class SecurityQuestion2Handler(SecurityQuestionHandler):
    def handle(self, email: str, answer: str) -> bool:
        return super().handle(email, answer, 1)

class SecurityQuestion3Handler(SecurityQuestionHandler):
    def handle(self, email: str, answer: str) -> bool:
        return super().handle(email, answer, 2)