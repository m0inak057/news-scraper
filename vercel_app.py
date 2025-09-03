import os
import sys
import json
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def handler(request):
    """
    Vercel serverless function handler
    """
    # Handle different request methods and paths
    method = request.get('httpMethod', 'GET')
    path = request.get('path', '/')
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle OPTIONS request (CORS preflight)
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Handle API scraping request
    if path.startswith('/api') and method == 'POST':
        try:
            # Parse request body
            body = request.get('body', '{}')
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
            
            url = data.get('url')
            
            if not url:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'URL is required.'})
                }
            
            # Scrape the website
            scrape_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=scrape_headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            headlines_tags = soup.select('h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, .title a, .headline a')
            
            results = []
            seen_links = set()
            
            for tag in headlines_tags:
                title = tag.get_text(strip=True)
                link = tag.get('href')
                
                if title and link and link not in seen_links:
                    full_link = urljoin(url, link)
                    results.append({'title': title, 'link': full_link})
                    seen_links.add(link)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(results)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': f'Failed to fetch the URL: {str(e)}'})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': f'An unexpected error occurred: {str(e)}'})
            }
    
    # Handle main page request
    elif path == '/' and method == 'GET':
        # Return the HTML content
        html_file = BASE_DIR / 'index.html'
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': html_content
            }
        except FileNotFoundError:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Page not found'})
            }
    
    # Handle favicon and other static requests
    elif path.startswith('/favicon') or path.startswith('/static'):
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Resource not found'})
        }
    
    # Default response
    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({'error': 'Not found'})
    }

# For compatibility with different Vercel function formats
app = handler
