from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods')
    food_name = models.CharField(max_length=255)
    serving_qty = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    serving_unit = models.CharField(max_length=50, default="serving")
    nf_calories = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    nf_protein = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    nf_total_carbohydrate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    nf_total_fat = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.food_name
