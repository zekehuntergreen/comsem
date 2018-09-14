import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ComSemApp.models import Expression
from django.core.files.base import ContentFile

class Command(BaseCommand):

    def handle(self, *args, **options):
        base_directory = os.path.join(settings.MEDIA_ROOT, "ExpressionReformulations")
        for root, directories, files in os.walk(base_directory):
            for directory in directories:
                base_expression_id = int(directory) * 1000
                for root, directories, files in os.walk(os.path.join(base_directory, directory)):
                    for file in files:
                        expression_id = base_expression_id + int(file.split(".")[0])
                        fullpath = os.path.join(root, file)

                        expression = Expression.objects.filter(id=expression_id).first()
                        if expression:
                            file_content = None
                            with open(fullpath, "r") as audio_file:
                                file_content = ContentFile(audio_file.read())
                            expression.audio.save(file_content, file_content)
                            expression.save()