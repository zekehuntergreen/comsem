from django.core.management.base import BaseCommand, CommandError
from ComSemApp.models import Expression, SequentialWords, Word, Tag

class Command(BaseCommand):
    help = 'Drops all data from SequentialWords, Word, and Tag tables, then takes each expression, tokenizes it using nltk and the CLAW5 tagset, and inserts the relevant information into those three tables'

    def handle(self, *args, **options):
        print('handle')
