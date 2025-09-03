import json
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["POST"])
def scrape_headlines(request):
    try:
        # Get the data sent from the frontend
        data = json.loads(request.body)
        url = data.get('url')

        # If no URL is provided, send back an error
        if not url:
            return JsonResponse({'error': 'URL is required.'}, status=400)

        # Standard scraping logic
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # A broad selector to find as many headlines as possible
        headlines_tags = soup.select('h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, .title a, .headline a')
        
        results = []
        seen_links = set()  # To avoid duplicates

        for tag in headlines_tags:
            title = tag.get_text(strip=True)
            link = tag.get('href')

            if title and link and link not in seen_links:
                full_link = urljoin(url, link)
                results.append({'title': title, 'link': full_link})
                seen_links.add(link)
        
        # Send the list of headlines back to the frontend as JSON
        return JsonResponse(results, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except requests.exceptions.RequestException as e:
        # Handle errors during the web request
        return JsonResponse({'error': f'Failed to fetch the URL: {str(e)}'}, status=500)
    except Exception as e:
        # Handle any other unexpected errors
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
