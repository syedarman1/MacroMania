from django.core.management.base import BaseCommand
from counter.models import Category, FoodItem
import requests

APP_ID = "df07473e"
APP_KEY = "a03761729ed0811e282d8d18a825da9e"

CATEGORY_FOOD_MAPPING = {
    'fruits': "Acai Berry,Ackee,Apple,Apricot,Asian Pear,Avocado,Banana,Blackberry,Blood Orange,Blueberry,Cherry,Coconut,Cranberry,Date,Dragon Fruit,Elderberry,Fig,Grape,Grapefruit,Guava,Jackfruit,Kiwi,Lemon,Lime,Mango,Melon,Nectarine,Orange,Papaya,Peach,Pear,Pineapple,Pomegranate,Raspberry,Strawberry,Tangerine,Watermelon",
    'vegetables': "Artichoke,Arugula,Asparagus,Beet,Broccoli,Cabbage,Carrot,Cauliflower,Celery,Chard,Cucumber,Eggplant,Green Bean,Kale,Leek,Lettuce,Mushroom,Onion,Parsnip,Pea,Potato,Radish,Spinach,Squash,Tomato,Zucchini",
    'salads': "Caesar Salad,Greek Salad,Caprese Salad,Garden Salad,Spinach Salad,Potato Salad,Coleslaw,Bean Salad,Nicoise Salad,Quinoa Salad",
    'grains-cereals': "Rice,Wheat,Oats,Barley,Quinoa,Corn,Couscous,Bulgur,Rye,Sorghum",
    'legumes': "Black Bean,Chickpea,Lentil,Pea,Red Kidney Bean,Pinto Bean,White Bean",
    'nuts-seeds-oils': "Almond,Walnut,Cashew,Pistachio,Flaxseed,Chia Seed,Pumpkin Seed,Sunflower Seed,Olive Oil,Canola Oil",
    'meat-poultry': "Chicken,Beef,Pork,Lamb,Turkey,Duck",
    'seafood': "Salmon,Tuna,Shrimp,Crab,Lobster,Scallop",
    'dairy': "Milk,Cheese,Yogurt,Butter,Ice Cream",
    'eggs': "Chicken Egg,Quail Egg",
    'baked-goods': "Bread,Bagel,Muffin,Croissant,Donut",
    'sweets-desserts': "Cake,Cookie,Pie,Pastry,Chocolate,Ice Cream,Pudding",
    'snacks': "Chips,Crackers,Popcorn,Nuts,Granola Bar",
    'beverages': "Water,Juice,Soda,Tea,Coffee,Energy Drink",
    'condiments-sauces': "Ketchup,Mustard,Mayonnaise,Hot Sauce,Barbecue Sauce,Soy Sauce",
    'fast-foods': "Burger,Fries,Pizza,Hot Dog,Taco,Burrito",
    'miscellaneous': "Spice,Herb,Sauce,Pickle"
}

class Command(BaseCommand):
    help = "Import food items from Nutritionix API for each category based on a curated list."

    def handle(self, *args, **options):
        for category in Category.objects.all():
            self.stdout.write(f"Importing foods for {category.name}...")
            food_list_str = CATEGORY_FOOD_MAPPING.get(category.slug)
            if not food_list_str:
                self.stdout.write(self.style.WARNING(f"No food mapping found for {category.name}"))
                continue
            food_names = [name.strip() for name in food_list_str.split(',')]
            for food_name in food_names:
                url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
                headers = {
                    "x-app-id": APP_ID,
                    "x-app-key": APP_KEY,
                    "Content-Type": "application/json"
                }
                data = {
                    "query": food_name,
                    "timezone": "US/Eastern"
                }
                try:
                    response = requests.post(url, headers=headers, json=data)
                    response.raise_for_status()
                    api_data = response.json()
                    if api_data.get("foods"):
                        detailed_food = api_data["foods"][0]
                        if not FoodItem.objects.filter(
                            category=category,
                            food_name=detailed_food.get("food_name", food_name)
                        ).exists():
                            FoodItem.objects.create(
                                category=category,
                                food_name=detailed_food.get("food_name", food_name),
                                serving_qty=detailed_food.get("serving_qty", 1.0),
                                serving_unit=detailed_food.get("serving_unit", "serving"),
                                nf_calories=detailed_food.get("nf_calories", 0),
                                nf_protein=detailed_food.get("nf_protein", 0),
                                nf_total_carbohydrate=detailed_food.get("nf_total_carbohydrate", 0),
                                nf_total_fat=detailed_food.get("nf_total_fat", 0)
                            )
                            self.stdout.write(self.style.SUCCESS(f"Imported {food_name}"))
                        else:
                            self.stdout.write(f"{food_name} already exists")
                    else:
                        self.stdout.write(self.style.WARNING(f"No data for {food_name}"))
                except requests.exceptions.RequestException as e:
                    self.stdout.write(self.style.ERROR(f"API error for {food_name}: {e}"))
            self.stdout.write(self.style.SUCCESS(f"Done importing for {category.name}\n"))
