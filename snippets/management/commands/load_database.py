import json

from snippets.models import Language, User
from django.core.management.base import BaseCommand
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Upload Languages to database from json file'

    def handle(self, *args, **kwargs):
        with open("dump_data.json", "r") as file:
            data = json.load(file)
            for language in data:
                obj, created = Language.objects.get_or_create(
                    name = language["fields"]["name"],
                    slug = language["fields"]["slug"]
                )

        self.stdout.write(self.style.HTTP_INFO('Done uploading languages'))

        try:
            User.objects.create_superuser(
                email="admin@admin.com",
                password="admin2025",
                username="adminUser"
            )

            self.stdout.write(self.style.HTTP_INFO (f'Admin user created'))
        except IntegrityError:
            self.stdout.write(self.style.HTTP_INFO (f'Admin user already exists'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error runnning command: {e}'))

        self.stdout.write(self.style.SUCCESS('Done uploading languages and admin user'))
