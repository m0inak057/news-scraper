import json
from urllib.parse import urljoin, parse_qs
import requests
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle GET requests
        if self.path == '/' or self.path == '':
            self.serve_html()
        elif self.path.startswith('/favicon'):
            self.send_404()
        else:
            self.send_404()
    
    def do_POST(self):
        # Handle POST requests for API
        if self.path.startswith('/api'):
            self.handle_scraping()
        else:
            self.send_404()
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_cors_headers()
        self.end_headers()
    
    def serve_html(self):
        try:
            # Read the HTML file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            html_file = os.path.join(current_dir, 'index.html')
            
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_404()
    
    def handle_scraping(self):
        try:
            # Get the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8'))
            url = data.get('url')
            
            if not url:
                self.send_json_response({'error': 'URL is required.'}, 400)
                return
            
            # Scrape the website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
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
            
            self.send_json_response(results, 200)
            
        except requests.exceptions.RequestException as e:
            self.send_json_response({'error': f'Failed to fetch the URL: {str(e)}'}, 500)
        except json.JSONDecodeError:
            self.send_json_response({'error': 'Invalid JSON data'}, 400)
        except Exception as e:
            self.send_json_response({'error': f'An unexpected error occurred: {str(e)}'}, 500)
    
    def send_json_response(self, data, status_code):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_404(self):
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Not found'}).encode('utf-8'))
