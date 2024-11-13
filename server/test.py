from newspaper import Article
from flask import Flask
from flask_cors import CORS

# Test newspaper
url = 'https://example.com'
article = Article(url)

print("All imports successful!")