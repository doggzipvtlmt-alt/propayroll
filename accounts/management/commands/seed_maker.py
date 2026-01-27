from django.core.management.base import BaseCommand

from core.db import ensure_maker_user


class Command(BaseCommand):
    help = 'Seed the default maker user.'

    def handle(self, *args, **options):
        ensure_maker_user()
        self.stdout.write(self.style.SUCCESS('Maker user seeded.'))
