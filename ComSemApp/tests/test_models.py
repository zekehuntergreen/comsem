from django.db.utils import IntegrityError
from django.db import transaction

from ComSemApp.models import *
from ComSemApp.libs.factories import BaseTestCase

class TestSpeakingPracticeAttempt(BaseTestCase):
    """
        Creates a test 
    """
    def setUp(self):
        self.expression = self.db_create_expression()
    
    def test_exception_on_null_fields(self):
        with transaction.atomic():
            self.assertRaises(IntegrityError, SpeakingPracticeAttempt.objects.create)
        with transaction.atomic():
            self.assertRaises(IntegrityError, SpeakingPracticeAttempt.objects.create, expression=self.expression)
        with transaction.atomic():
            self.assertRaises(IntegrityError, SpeakingPracticeAttempt.objects.create, expression=self.expression, correct=90)
        with transaction.atomic():
            self.assertRaises(IntegrityError, SpeakingPracticeAttempt.objects.create, expression=self.expression, wpm=100)
        with transaction.atomic():
            self.assertRaises(IntegrityError, SpeakingPracticeAttempt.objects.create, correct=90)
        with transaction.atomic():
            self.assertRaises(IntegrityError, SpeakingPracticeAttempt.objects.create, correct=90, wpm=100)
        with transaction.atomic():
            self.assertRaises(IntegrityError, SpeakingPracticeAttempt.objects.create, wpm=100)

    def test_no_error_with_allowed_fields_null(self):
        with transaction.atomic():
            self.assertIsNotNone(SpeakingPracticeAttempt.objects.create(expression=self.expression, correct=90, wpm=100))
