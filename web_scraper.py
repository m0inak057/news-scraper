import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_all_news(url):
    """
    Fetches and displays all possible headlines from a given news website URL.
    
    NOTE: This scraper uses a broad set of generic tags (h1-h6, .title, .headline) 
    to find headlines. This is a guess and may not work perfectly for all websites, 
    as each site has a unique HTML structure. For best results, you may still need 
    to inspect the target website's HTML and adjust the selector.
    """
    try:
        # Set a User-Agent header to mimic a browser, which is good practice
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"🔎 Fetching news from: {url}")
        # Set a timeout to prevent the script from hanging indefinitely
        response = requests.get(url, headers=headers, timeout=10)
        # This will raise an HTTPError for bad responses (4xx or 5xx status codes)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to retrieve data: {e}")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # --- IMPORTANT ---
    # The selector below is a more comprehensive GENERIC guess. It looks for links 
    # inside any heading tag (<h1> to <h6>) and elements with common class names 
    # like 'title' or 'headline'.
    headlines = soup.select('h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, .title a, .headline a')

    if not headlines:
        print("\n⚠️ No headlines found with the current generic selectors.")
        print("   Consider inspecting the website's HTML to find a more specific selector.")
        return

    print(f"\n🧾 Found {len(headlines)} possible headlines:\n")
    count = 0
    printed_links = set()  # Use a set to keep track of and avoid duplicate links

    for headline in headlines:
        # Extract the text and clean up whitespace
        title = headline.get_text(strip=True)
        # Extract the href attribute (the link)
        link = headline.get('href')

        # Filter out any empty titles or links, and ignore duplicates
        if title and link and link not in printed_links:
            # Convert relative URLs (like '/news/story') to absolute URLs
            full_link = urljoin(url, link)
            
            print(f"📰 {title}")
            print(f"   ► Link: {full_link}\n")
            
            # Add the link to our set of printed links to avoid re-printing it
            printed_links.add(link)
            count += 1
    
    if count == 0:
        print("🤷 No valid headlines could be extracted after filtering.")
    else:
        print(f"✨ Successfully extracted {count} unique headlines.")

# --- Run the scraper ---
if __name__ == "__main__":
    # Prompt the user to enter the website URL
    target_url = input("Enter the news website URL to scrape (e.g., https://www.bbc.com/news): ")
    
    if target_url:
        fetch_all_news(target_url)
    else:
        print("No URL entered. Exiting.")
