from django.shortcuts import render
import requests
import json

def home(request):
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
            print(e)  # Log the error
            return render(request, 'home.html', {'api': 'An error occurred while fetching the data.'})
        else:
            if api:
                return render(request, 'home.html', {'api': api})  
            else:
                return render(request, 'home.html', {'api': 'No data found for the given query.'})
    else:
        return render(request, 'home.html', {'query': 'Enter a valid query'})
