import pandas as pd
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из CSV в бд'

    def handle(self, *args, **options):
        '''Иморт данных для ингредиентов'''
        df = pd.read_csv('data/ingredients.csv')
        for import_name, import_measurement_unit in zip(
                df.name, df.measurement_unit):
            models = Ingredient(
                name=import_name, measurement_unit=import_measurement_unit)
            models.save()
