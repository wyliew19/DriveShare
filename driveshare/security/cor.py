from typing import Optional
from driveshare.utils.database import DatabaseHandler

class SecurityQuestion:
    def __init__(self, question, answer, next_question=None):
        self.question = question
        self.answer = answer
        self.next_question = next_question

    def check_answer(self, answer):
        return answer == self.answer
    
    def get_next_question(self):
        return self.next_question
        
    def set_next_question(self, next_question):
        if self.next_question is None:
            self.next_question = next_question
        else:
            self.next_question.set_next_question(next_question)


    

    def __str__(self):
        return self.question


class SecurityQuestionHandler:
    def __init__(self, email):
        self.email = email
        # TODO: Get security question answers from database using email
        self.questions = SecurityQuestion('What is your favorite color?', 'blue')
        self.questions.set_next_question(SecurityQuestion('What is your favorite animal?', 'dog'))
        self.questions.set_next_question(SecurityQuestion('What is your favorite food?', 'pizza'))

    def check_answer(self, answer):
         if self.questions.check_answer(answer):
            self.questions = self.questions.get_next_question()
            return True
         
         return False

    def at_end(self):
        return self.questions is None
