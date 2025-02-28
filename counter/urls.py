from django.urls import path
from . import views

urlpatterns = [
    path('', views.calorie_tracker, name='calorie_tracker'),
    path('bmi/', views.bmi_calculator, name='bmi_calculator'),
    path('tdee/', views.tdee_calculator, name='tdee_calculator'),
    path('contact/', views.contact, name='contact'),
    path('macromania/', views.food_database, name='food_database'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
]
