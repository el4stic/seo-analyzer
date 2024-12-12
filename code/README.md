# Google SERP Analyzer

This Python application provides a web interface for analyzing Google search results using SerpAPI. It fetches detailed information from each result page, including meta titles, meta descriptions, H1 tags, H2 tags, and links.

## Features

- 🌐 Modern web interface built with Streamlit
- 🔍 Analyze top 10 Google search results
- 📊 View results in three different formats:
  - Summary statistics
  - Detailed view with expandable sections
  - Raw JSON data
- 💾 Automatic saving of results with timestamps
- 🔒 Secure API key handling

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your SerpAPI key:
```
SERPAPI_KEY=your_serpapi_key_here
```

## Usage

### Web Interface (Recommended)

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

3. Enter your SerpAPI key in the sidebar (if not already in `.env`)

4. Enter your search query and click "Analyze Search Results"

### Command Line Interface

Alternatively, you can still use the command-line version:

```bash
python serp_scraper.py
```

## Output

Results are saved as JSON files with timestamps (e.g., `search_results_20231225_143022.json`) with the following structure:
```json
[
  {
    "title": "Page title",
    "meta_description": "Meta description/snippet",
    "url": "Page URL",
    "h1_tags": ["H1 tag contents"],
    "h2_tags": ["H2 tag contents"],
    "links": ["URLs found on the page"]
  }
]
``` 