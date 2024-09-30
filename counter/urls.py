from django.urls import path
from .  import views

urlpatterns = [
    path('', views.home, name ='home'),
    path('bmi/', views.bmi_calculator, name='bmi_calculator'), 
    path('tdee/', views.tdee_calculator, name='tdee_calculator'),  
]
