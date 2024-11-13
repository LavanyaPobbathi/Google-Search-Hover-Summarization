# Google Search Hover AI Summarizer 📚

**Google Search Hover AI Summarizer** is a Chrome extension that provides AI-powered summaries for search results on Google. Hover over a search result, and a summary appears in a sleek, informative popup without having to leave the search page. This project leverages Flask, Selenium, and Hugging Face’s LLaMA and BART models for real-time, accurate article summarization.

## 🎯 Project Overview
The Google Search Hover Summarizer enhances your browsing experience by quickly summarizing articles right on the Google search page. This tool is perfect for researchers, students, and professionals looking to save time by reviewing concise summaries before committing to a full read.

## 🚀 Key Features
- **Seamless Integration**: Summaries display instantly on hover.
- **AI-Powered Summarization**: Uses Hugging Face models for quality summaries.
- **Dynamic Content Handling**: Falls back to Selenium for dynamic web pages.
- **User-Friendly Design**: Clean, responsive popup with summary, reading time, and an "AI Generated" badge.

## 📂 Project Structure
- **extension**: Contains the Chrome extension’s files.
  - `content.js`: Manages hover events, calls the backend, and displays summaries in the popup.
  - `styles.css`: Custom styles for the popup.
  - `manifest.json`: Extension configuration.
- **server**: Contains Flask server files.
  - `app.py`: Processes URLs, fetches content, generates summaries, and returns JSON.
  - `.env`: Stores API tokens.
- **venv**: Python virtual environment.

## 🛠️ Setup

### Set Up the Flask Server
**Create a `.env` file** with your Hugging Face token:
   ```makefile
   HUGGINGFACE_TOKEN=your_token
  ```
### Load the Chrome Extension
  - Open chrome://extensions in Chrome.
  - Enable "Developer mode" and click "Load unpacked."
    
## Install dependencies:
   ```makefile
   pip install -r requirements.txt
   ```
### Start the Flask server:
  ```makefile
  python app.py
  ```

### Select the extension folder.
Perform a Google search, and hover over any search result to see the summarizer in action!

## 📝 Demo
Check out this demo video to see Google Search Hover AI Summarizer in action! [![Watch the demo](thumbnail.png)](https://github.com/LavanyaPobbathi/Google-Search-Hover-Summarization/blob/main/demo.mp4)

![image](https://github.com/user-attachments/assets/70a3f7ef-9b5f-4ece-8e23-88b3a033c03f)
![image](https://github.com/user-attachments/assets/dd083a53-3ad0-4402-bd38-de6c463dd0b2)

### 🤖 Technology Stack
 - **Backend:** Python, Flask, Selenium, BeautifulSoup 
 - **Large Language Models:** Hugging Face (LLaMA, BART models)
 - **Frontend:** JavaScript, HTML, CSS

### 🙌 Acknowledgments
  - Hugging Face for the powerful language models
  - Google Search for providing content-rich results to test the extension
