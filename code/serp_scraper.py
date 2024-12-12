import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
from typing import Dict, List
import time

def get_page_content(url: str) -> Dict:
    """Scrape internal content of a webpage."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return {
            'h1_tags': [h1.get_text(strip=True) for h1 in soup.find_all('h1')],
            'h2_tags': [h2.get_text(strip=True) for h2 in soup.find_all('h2')],
            'links': [a.get('href') for a in soup.find_all('a', href=True)]
        }
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {
            'h1_tags': [],
            'h2_tags': [],
            'links': []
        }

def search_and_analyze(query: str, api_key: str) -> List[Dict]:
    """Perform Google search and analyze results using SerpAPI."""
    # Build the URL for SerpAPI
    base_url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": 10,  # Number of results
        "gl": "us",  # Country to search from
        "hl": "en"   # Language
    }
    
    try:
        # Make the API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = response.json()
        
        detailed_results = []
        
        # Process organic results
        for result in results.get('organic_results', [])[:10]:
            print(f"Processing: {result.get('title', 'No title')}")
            
            detailed_result = {
                'title': result.get('title'),
                'meta_description': result.get('snippet'),
                'url': result.get('link')
            }
            
            # Get internal content
            internal_content = get_page_content(result['link'])
            detailed_result.update(internal_content)
            
            detailed_results.append(detailed_result)
            time.sleep(1)  # Be nice to servers
        
        return detailed_results
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing API response: {str(e)}")
        return []
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return []

def main():
    load_dotenv()
    api_key = os.getenv('SERPAPI_KEY')
    
    if not api_key:
        print("Please set your SERPAPI_KEY in the .env file")
        return
    
    query = input("Enter your search query: ")
    results = search_and_analyze(query, api_key)
    
    # Save results to JSON file
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nAnalysis complete! Results saved to search_results.json")
    print(f"Processed {len(results)} pages")

if __name__ == "__main__":
    main() 