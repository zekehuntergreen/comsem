from ComSemApp.tests.factories import Factory
from django.test import TestCase
from django.test import Client

class BaseTestCase(Factory, TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.client = Client()