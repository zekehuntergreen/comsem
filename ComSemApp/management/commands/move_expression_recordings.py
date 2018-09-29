import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ComSemApp.models import Expression, StudentAttempt, audio_directory_path
from django.core.files.base import ContentFile
from shutil import copyfile

class Command(BaseCommand):

    def handle(self, *args, **options):
        objects = {
            "ExpressionReformulations": Expression,
            "AttemptReformulations": StudentAttempt,
        }
        media_root = settings.MEDIA_ROOT

        for file_name, model_class in objects.items():
            print("copying ", model_class)

            base_directory = os.path.join(media_root, file_name)

            tried, copied = 0, 0

            for root, directories, files in os.walk(base_directory):
                for directory in directories:
                    base_obj_id = int(directory) * 1000
                    for root, directories, files in os.walk(os.path.join(base_directory, directory)):
                        for file in files:

                            obj_id = base_obj_id + int(file.split(".")[0])
                            obj = model_class.objects.filter(id=obj_id).first()

                            tried += 1
                            if obj:
                                old_path = os.path.join(root, file)
                                new_path = audio_directory_path(None, obj)
                                new_path_full = media_root + "/" + new_path
                                print(old_path)
                                print(new_path)
                                copyfile(old_path, new_path_full)
                                obj.audio.name = new_path
                                obj.save()
                                copied += 1

            orphans = tried - copied
            print("Tried ", tried)
            print("Copied ", copied)
            print(f"({orphans} orphan files)")
