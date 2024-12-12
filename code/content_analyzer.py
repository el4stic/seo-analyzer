import os
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
from typing import Dict, List
import time
import json
import re

def clean_text(text: str) -> str:
    """Clean text from special characters that might cause formatting issues."""
    return re.sub(r'[^\w\s\u0590-\u05FF,.?!-]', '', text)

def get_page_content(url: str) -> Dict:
    """Scrape detailed content from a webpage."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get meta tags
        meta_description = soup.find('meta', {'name': 'description'})
        meta_description = meta_description['content'] if meta_description else ''
        
        # Get title
        title = soup.title.string if soup.title else ''
        
        # Get main content
        main_content = ' '.join([p.get_text(strip=True) for p in soup.find_all(['p', 'article', 'section', 'div']) if len(p.get_text(strip=True)) > 50])
        
        # Clean all text fields
        return {
            'title': clean_text(title),
            'meta_description': clean_text(meta_description),
            'h1_tags': [clean_text(h1.get_text(strip=True)) for h1 in soup.find_all('h1')],
            'h2_tags': [clean_text(h2.get_text(strip=True)) for h2 in soup.find_all('h2')],
            'main_content': clean_text(main_content[:1000]),  # First 1000 chars for analysis
            'url': url
        }
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {
            'title': '',
            'meta_description': '',
            'h1_tags': [],
            'h2_tags': [],
            'main_content': '',
            'url': url
        }

def analyze_serp_content(query: str, serpapi_key: str, claude_key: str) -> Dict:
    """Analyze search results and provide content recommendations."""
    # Initialize SerpAPI search
    params = {
        "engine": "google",
        "q": query,
        "api_key": serpapi_key,
        "num": 10,
        "gl": "il",  # Israel
        "hl": "he"   # Hebrew
    }
    
    try:
        # Get search results
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        results = response.json()
        
        # Analyze each result
        detailed_results = []
        for result in results.get('organic_results', [])[:10]:
            print(f"Processing: {result.get('title', 'No title')}")
            content = get_page_content(result['link'])
            detailed_results.append(content)
            time.sleep(1)  # Be nice to servers
        
        # Prepare data for Claude analysis
        analysis_prompt = f"""בתור מומחה SEO ואסטרטג תוכן, נתח את תוצאות החיפוש הבאות עבור מילת החיפוש: {query}

הנה התוצאות שנמצאו:
{json.dumps(detailed_results, ensure_ascii=False, indent=2)}

אנא ספק ניתוח מפורט שעונה על השאלות הבאות:

1. מהו סוג התוכן שמדורג הכי טוב בתוצאות (מאמר, דף שירות, דף מוצר, דף קטגוריה וכו')?
2. האם התוכן צריך להיות ספציפי מאוד או כללי יותר?
3. מהם הנושאים העיקריים שצריך לכסות בהתבסס על הדפים המתחרים?
4. האם כדאי להתמקד רק במילת החיפוש או להרחיב לנושאים קשורים?
5. מהו המבנה המומלץ לדף?

אנא ענה בפורמט הבא:

סוג התוכן המומלץ: [תשובה]
רמת הספציפיות: [תשובה]
נושאים מומלצים:
- [נושא 1]
- [נושא 2]
- [נושא 3]
מיקוד התוכן: [תשובה]
המלצה למבנה התוכן: [תשובה]
הסבר להמלצות: [תשובה]

חשוב: אנא ענה בעברית בלבד."""

        # Get Claude's analysis
        try:
            client = Anthropic(
                api_key=claude_key,
                default_headers={"anthropic-version": "2023-06-01"}
            )
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }],
                max_tokens=1024,
                system="אתה מומחה SEO ואסטרטג תוכן. תספק המלצות מפורטות בעברית בלבד."
            )
        except Exception as e:
            print(f"Error with Claude API: {str(e)}")
            raise Exception(f"שגיאה בתקשורת עם Claude API: {str(e)}")
        
        # Parse Claude's response
        analysis = response.content[0].text
        
        # Initialize variables
        content_type = ""
        specificity = ""
        recommended_sections = []
        content_focus = ""
        structure_recommendation = ""
        reasoning = ""
        
        # Split response into lines and process
        current_section = ""
        lines = analysis.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("סוג התוכן המומלץ:"):
                content_type = line.split(":", 1)[1].strip()
                current_section = "content_type"
            elif line.startswith("רמת הספציפיות:"):
                specificity = line.split(":", 1)[1].strip()
                current_section = "specificity"
            elif line.startswith("נושאים מומלצים:"):
                current_section = "sections"
            elif line.startswith("מיקוד התוכן:"):
                content_focus = line.split(":", 1)[1].strip()
                current_section = "focus"
            elif line.startswith("המלצה למבנה התוכן:"):
                structure_recommendation = line.split(":", 1)[1].strip()
                current_section = "structure"
            elif line.startswith("הסבר להמלצות:"):
                reasoning = line.split(":", 1)[1].strip()
                current_section = "reasoning"
            elif current_section == "sections" and line.startswith("-"):
                recommended_sections.append(line[1:].strip())
            elif current_section == "reasoning":
                reasoning += " " + line
        
        analysis_json = {
            "content_type": content_type or "לא נמצא סוג תוכן",
            "specificity": specificity or "לא נמצאה רמת ספציפיות",
            "recommended_sections": recommended_sections or ["לא נמצאו נושאים מומלצים"],
            "content_focus": content_focus or "לא נמצא מיקוד תוכן",
            "structure_recommendation": structure_recommendation or "לא נמצאה המלצת מבנה",
            "reasoning": reasoning or "לא נמצא הסבר"
        }
        
        return {
            "query": query,
            "analysis": analysis_json,
            "analyzed_urls": [result.get('link') for result in results.get('organic_results', [])[:10]]
        }
        
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        return {
            "error": str(e),
            "query": query
        } 