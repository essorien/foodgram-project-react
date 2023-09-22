import json
from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

FILE = f'{settings.BASE_DIR}/data/ingredients.json'


def import_json_data():
    with open(FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for note in data:
            Ingredient.objects.get_or_create(**note)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            import_json_data()
        except Exception as error:
            self.stdout.write(
                self.style.WARNING(f'Сбой в работе импорта: {error}.'))
        else:
            self.stdout.write(self.style.SUCCESS('Загрузка данных завершена.'))
