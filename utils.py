import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import requests
from bs4 import BeautifulSoup
import logging
from googlesearch import search

# Load environment variables
load_dotenv()

# Retrieve token from environment variables
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not token:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN is not set or empty.")

# Debug: Print token (partially masked)
print(f"Token: {token[:5]}...{token[-5:] if len(token) > 10 else ''}")

# Initialize HuggingFaceEndpoint client for GPT-2
llm = HuggingFaceEndpoint(
    repo_id="gpt2",
    temperature=0.7,  # Pass temperature directly
    huggingfacehub_api_token=token,
    model_kwargs={'max_length': 100}  # Pass max_length in model_kwargs
)

# Default User-Agent
DEFAULT_USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

def retrieve_web_content(query):
    try:
        # Use googlesearch-python library to perform Google search
        search_results = search(query, num_results=3)

        content = []
        for link in search_results:
            try:
                page_response = requests.get(link, headers={"User-Agent": DEFAULT_USER_AGENT}, timeout=5)
                page_response.raise_for_status()
                page_soup = BeautifulSoup(page_response.text, 'html.parser')

                # Extract text from paragraphs and headings
                text = ' '.join([p.get_text() for p in page_soup.find_all(['p', 'h1', 'h2', 'h3'])])
                content.append(text)
            except Exception as e:
                logging.error(f"Error retrieving content from {link}: {str(e)}")

        return ' '.join(content)[:500]  # Limit content to 500 characters
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error in retrieve_web_content: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Error in retrieve_web_content: {str(e)}")
        raise

def generate_response(query, chat_history):
    try:
        # Retrieve web content
        web_content = retrieve_web_content(query)
        logging.info(f"Retrieved web content: {web_content}")

        # Create a prompt template
        prompt_template = """
        You are an AI assistant tasked with answering questions based on web content.
        Use the following retrieved