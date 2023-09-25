from django.core.management import BaseCommand

from recipes.models import RecipeTag


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        tags = (
            ('Завтрак', '#FF5733', 'breakfast'),
            ('Обед', '#008000', 'lunch'),
            ('Ужин', '#FF0000', 'dinner'),
        )
        for tag in tags:
            name, color, slug = tag
            RecipeTag.objects.get_or_create(
                name=name,
                color=color,
                slug=slug
            )
        self.stdout.write(self.style.SUCCESS('Тэги добавлены.'))