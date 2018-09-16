import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ComSemApp.models import Expression, audio_directory_path
from django.core.files.base import ContentFile
from shutil import copyfile

class Command(BaseCommand):

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        base_directory = os.path.join(media_root, "ExpressionReformulations")

        tried = 0
        copied = 0

        for root, directories, files in os.walk(base_directory):
            for directory in directories:
                base_expression_id = int(directory) * 1000
                for root, directories, files in os.walk(os.path.join(base_directory, directory)):
                    for file in files:

                        expression_id = base_expression_id + int(file.split(".")[0])
                        expression = Expression.objects.filter(id=expression_id).first()

                        tried += 1
                        if expression:
                            old_path = os.path.join(root, file)
                            new_path = audio_directory_path(None, expression)
                            new_path_full = media_root + "/" + new_path
                            print(old_path)
                            print(new_path)
                            copyfile(old_path, new_path_full)
                            expression.audio.name = new_path
                            expression.save()
                            copied += 1
                            
        print("Tried ", tried)
        print("Copied", copied)
