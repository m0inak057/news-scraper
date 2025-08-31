from flask import Flask, request, jsonify
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Initialize the Flask application
app = Flask(__name__)

# This is now the ONLY route in your API file. 
# Vercel's routing will ensure any request to /api/... is sent here.
@app.route('/', methods=['POST'])
def scrape():
    # Get the data sent from the frontend
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
        
    url = data.get('url')

    # If no URL is provided, send back an error
    if not url:
        return jsonify({'error': 'URL is required.'}), 400

    try:
        # Standard scraping logic
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an error for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # A broad selector to find as many headlines as possible
        headlines_tags = soup.select('h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, .title a, .headline a')
        
        results = []
        seen_links = set() # To avoid duplicates

        for tag in headlines_tags:
            title = tag.get_text(strip=True)
            link = tag.get('href')

            if title and link and link not in seen_links:
                full_link = urljoin(url, link)
                results.append({'title': title, 'link': full_link})
                seen_links.add(link)
        
        # Send the list of headlines back to the frontend as JSON
        return jsonify(results)

    except requests.exceptions.RequestException as e:
        # Handle errors during the web request
        return jsonify({'error': f'Failed to fetch the URL: {str(e)}'}), 500
    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
