from django.db.utils import IntegrityError
from django.db import transaction
from django.core.exceptions import ValidationError

from decimal import InvalidOperation

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
        self.assertIsNotNone(SpeakingPracticeAttempt.objects.create(expression=self.expression, correct=90, wpm=100))

    def test_exception_on_out_of_range_values(self):
        # wpm too high
        with transaction.atomic():
            self.assertRaises(InvalidOperation, SpeakingPracticeAttempt.objects.create, expression=self.expression, correct=90, wpm=1000)
        # wpm too low (negative)
        with transaction.atomic():
            self.assertRaises(ValidationError, SpeakingPracticeAttempt.objects.create(expression=self.expression, correct=90, wpm=-1).full_clean)
        # correct too high
        with transaction.atomic():
            self.assertRaises(ValidationError, SpeakingPracticeAttempt.objects.create(expression=self.expression, correct=500, wpm=100).full_clean)
        # correct too low (negative)
        with transaction.atomic():
            self.assertRaises(ValidationError, SpeakingPracticeAttempt.objects.create(expression=self.expression, correct=-1, wpm=100).full_clean)