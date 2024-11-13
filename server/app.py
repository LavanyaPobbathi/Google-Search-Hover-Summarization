from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import json
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

app = Flask(__name__)
CORS(app)

HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
LLAMA_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
BART_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def get_text_with_selenium(url):
    driver = None
    try:
        print("Initializing Selenium...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"Fetching URL with Selenium: {url}")
        driver.get(url)
        
        # Wait for content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Try to find main content
        content_selectors = [
            "article",
            "main",
            ".content",
            ".article-content",
            "#content",
            "body"
        ]
        
        text = ""
        for selector in content_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    text = elements[0].text
                    break
            except:
                continue
                
        if not text:
            text = driver.find_element(By.TAG_NAME, "body").text
            
        print(f"Extracted text length: {len(text)}")
        return text[:4000]  # Limit text length
        
    except Exception as e:
        print(f"Selenium Error: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()

def get_text_with_requests(url):
    try:
        print(f"Fetching URL with requests: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        print(f"Extracted text length: {len(text)}")
        
        return text[:4000] if len(text) > 50 else None
        
    except Exception as e:
        print(f"Requests Error: {str(e)}")
        return None

def generate_summary_with_llama(text):
    try:
        prompt = f"""Analyze and summarize this article as if you're explaining it to someone who found it in a Google search:

{text}

Write a comprehensive summary that:
1. Begins with "This article discusses" or "This article explores" or "This article explains"
2. Clearly states what the article is about
3. Highlights the main points and key insights
4. Explains why this information is valuable or useful
5. Uses natural, engaging language
6. Provides enough context to understand the topic

Remember: Write as if you're helping someone decide if this article is worth reading. Make it informative and helpful.

Summary:"""
        
        print("Trying Llama model...")
        response = requests.post(
            LLAMA_API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 250,  # Increased for more comprehensive summaries
                    "min_new_tokens": 100,  # Increased minimum length
                    "temperature": 0.4,
                    "do_sample": True,
                    "top_p": 0.95,
                    "repetition_penalty": 1.2,
                    "stop": ["\n\n", "Note:", "Remember:"]
                }
            },
            timeout=30
        )
        
        print(f"Llama API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            return None
            
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            summary = result[0].get('generated_text', '').strip()
            
            # Clean up the summary
            summary = summary.split('Summary:')[-1].strip()
            
            # Enhanced cleaning
            unwanted_phrases = [
                "This summary",
                "In conclusion",
                "To summarize",
                "Note:",
                "Remember:",
                "_______"
            ]
            
            for phrase in unwanted_phrases:
                summary = summary.replace(phrase, '').strip()
            
            # Remove any special characters
            import re
            summary = re.sub(r'[_\-=]{2,}', '', summary)
            summary = re.sub(r'\s+', ' ', summary).strip()
            
            # Ensure it starts correctly
            starter_phrases = [
                "this article discusses",
                "this article explores",
                "this article explains",
                "this article describes"
            ]
            
            if not any(summary.lower().startswith(phrase) for phrase in starter_phrases):
                best_starter = "This article discusses"
                summary = f"{best_starter} {summary[0].lower()}{summary[1:]}"
            
            # Ensure proper sentence structure
            sentences = summary.split('.')
            cleaned_sentences = [s.strip() for s in sentences if s.strip()]
            summary = '. '.join(cleaned_sentences) + '.'
            
            # Additional formatting cleanup
            summary = summary.replace('..','.').replace('. .','.').replace('...','.').strip()
            
            # Length check
            if len(summary) < 100:  # Increased minimum length requirement
                return None
                
            return summary
            
        return None
        
    except Exception as e:
        print(f"Llama Error: {str(e)}")
        return None

def generate_summary_with_bart(text):
    try:
        # Create a more engaging prompt for BART
        enhanced_text = f"""Focus on what's important for readers searching for this topic:

{text}

Provide a detailed, useful summary that explains what this article covers and why it matters."""

        print("Trying BART model...")
        response = requests.post(
            BART_API_URL,
            headers=headers,
            json={
                "inputs": enhanced_text,
                "parameters": {
                    "max_length": 150,  # Increased for more detail
                    "min_length": 100,  # Increased minimum length
                    "do_sample": True,
                    "temperature": 0.4,
                    "num_beams": 4,
                    "early_stopping": True
                }
            },
            timeout=30
        )
        
        print(f"BART API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            return None
            
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            summary = result[0].get('summary_text', '').strip()
            if summary:
                # Format consistently
                if not any(summary.lower().startswith(phrase) for phrase in ["this article", "the article"]):
                    summary = "This article discusses " + summary[0].lower() + summary[1:]
                
                # Ensure proper ending
                if not summary.endswith('.'):
                    summary += '.'
                
                # Clean up any double periods
                summary = summary.replace('..', '.').replace('. .', '.')
                return summary
            
        return None
        
    except Exception as e:
        print(f"BART Error: {str(e)}")
        return None
    
def generate_summary(text):
    try:
        # Try Llama first
        summary = generate_summary_with_llama(text)
        
        # If Llama fails, try BART
        if not summary:
            print("Llama failed or produced poor summary, trying BART...")
            summary = generate_summary_with_bart(text)
            
        return summary or "Could not generate a meaningful summary"
        
    except Exception as e:
        print(f"Error in generate_summary: {str(e)}")
        return f"Error generating summary: {str(e)}"
    
@app.route('/summarize', methods=['POST'])
def summarize():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        print(f"\n=== New Request for URL: {url} ===")
        
        text = get_text_with_requests(url) or get_text_with_selenium(url)
        
        if not text:
            return jsonify({'error': 'Could not extract text from URL'}), 400
            
        # Generate summary
        summary = generate_summary(text)
        
        # Extract key points (you can modify this based on your needs)
        #key_points = [
        #    "First key point from the article",
        #    "Second important insight",
        #    "Third significant finding"
        #]
        
        # Calculate stats
        words = text.split()
        stats = {
            "read_time": len(words) // 150,  # Assuming 200 words per minute
            "topic": "Technology"  # You can implement topic detection
        }
        
        return jsonify({
            'summary': summary,
            #'key_points': key_points,
            'stats': # It looks like the code is attempting to comment out the line "stats" using the "#" symbol in Python. However, the code is not valid as it is missing the actual comment symbol "#".
            stats
        })
    
    except Exception as e:
        print(f"Error in summarize endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
"""
@app.route('/summarize', methods=['POST'])
def summarize():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        print(f"\n=== New Request for URL: {url} ===")
        
        # Try requests first
        text = get_text_with_requests(url)
        
        # If requests fails, try Selenium
        if not text:
            print("Requests failed, trying Selenium...")
            text = get_text_with_selenium(url)
            
        if not text:
            return jsonify({'error': 'Could not extract text from URL'}), 400
            
        summary = generate_summary(text)
        return jsonify({'summary': summary})
    
    except Exception as e:
        print(f"Error in summarize endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500
"""
if __name__ == '__main__':
    print("\n=== Starting Server ===")
    print(f"CORS enabled: {bool(CORS)}")
    print(f"Hugging Face token present: {bool(HUGGINGFACE_TOKEN)}")
    app.run(debug=True, port=5001)