from django.shortcuts import render
import requests
import json

def home(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query='
        try:
            api_request = requests.get(api_url + query, headers={'X-Api-Key': '5tHy5tgQGAzIClNlzySJxRHAsPkZUmJ0FZvJ0g7k'})
            # Check if the request was successful
            api_request.raise_for_status()
            api = json.loads(api_request.content)
        except requests.exceptions.RequestException as e:
            # Log the error
            print(e)
            # Return the error to the template
            return render(request, 'home.html', {'api': 'An error occurred while fetching the data.'})
        else:
            # Check if the API returned data
            if api:
                return render(request, 'home.html', {'api': api})
            else:
                return render(request, 'home.html', {'api': 'No data found for the given query.'})
    else:
        # This will handle GET requests
        return render(request, 'home.html', {'query': 'Enter a valid query'})
