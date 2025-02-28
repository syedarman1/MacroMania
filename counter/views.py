from django.shortcuts import render, get_object_or_404
import requests
from .models import Category, FoodItem

def food_database(request):
    categories = Category.objects.all()
    return render(request, 'food_database.html', {'categories': categories})

def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    local_foods = (
        category.foods
        .exclude(nf_calories=0)
        .exclude(food_name__isnull=True)
        .exclude(food_name__exact='')
        .order_by('food_name')
    )

    if local_foods:
        foods = list(local_foods)
    else:
        category_mapping = {
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
        search_term = category_mapping.get(category.slug, category.name)
        api_url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
        headers = {
            'x-app-id': 'df07473e',
            'x-app-key': 'a03761729ed0811e282d8d18a825da9e',
            'Content-Type': 'application/json'
        }
        food_names = [name.strip() for name in search_term.split(',')]
        foods = []

        for food_name in food_names:
            data = {
                "query": food_name,
                "timezone": "US/Eastern"
            }
            try:
                response = requests.post(api_url, headers=headers, json=data)
                response.raise_for_status()
                api_data = response.json()
                if api_data.get("foods"):
                    detailed_food = api_data["foods"][0]
                    cleaned_name = detailed_food.get("food_name", "").strip()
                    if cleaned_name and detailed_food.get("nf_calories", 0) > 0:
                        foods.append(detailed_food)

                        if not FoodItem.objects.filter(
                            category=category,
                            food_name=cleaned_name
                        ).exists():
                            FoodItem.objects.create(
                                category=category,
                                food_name=cleaned_name,
                                serving_qty=detailed_food.get("serving_qty", 1.0),
                                serving_unit=detailed_food.get("serving_unit", "serving"),
                                nf_calories=detailed_food.get("nf_calories", 0),
                                nf_protein=detailed_food.get("nf_protein", 0),
                                nf_total_carbohydrate=detailed_food.get("nf_total_carbohydrate", 0),
                                nf_total_fat=detailed_food.get("nf_total_fat", 0)
                            )
                    else:
                        print(f"Skipping {food_name}: zero calories or blank name.")
                else:
                    print(f"No foods returned for {food_name}")
            except requests.exceptions.RequestException as e:
                print(f"API Error for {food_name}: {e}")

        foods = sorted(foods, key=lambda x: x.get("food_name", ""))

    return render(request, 'category_detail.html', {
        'category': category,
        'foods': foods,
    })


def calorie_tracker(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        api_url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
        headers = {
            'x-app-id': 'df07473e',
            'x-app-key': 'a03761729ed0811e282d8d18a825da9e',
            'Content-Type': 'application/json'
        }
        data = {
            "query": query,
            "timezone": "US/Eastern"
        }
        try:
            api_request = requests.post(api_url, headers=headers, json=data)
            api_request.raise_for_status()
            api = api_request.json()
        except requests.exceptions.RequestException as e:
            print("Calorie Tracker API Error:", e)
            return render(request, 'calorie_tracker.html', {'api': 'An error occurred while fetching the data.'})
        else:
            return render(request, 'calorie_tracker.html', {'api': api})
    else:
        return render(request, 'calorie_tracker.html', {'query': 'Enter a valid query'})


def bmi_calculator(request):
    return render(request, 'bmi.html')


def tdee_calculator(request):
    return render(request, 'tdee.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(f"Name: {name}, Email: {email}, Message: {message}")
        return render(request, 'contact.html', {'success': 'Your message has been sent!'})
    return render(request, 'contact.html')
