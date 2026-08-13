# Import LangChain's decorator that turns a normal Python function into a tool object.
from langchain.tools import tool

# Import the standard HTTP library to make GET requests to a public page.
import requests

# Import BeautifulSoup to parse and clean HTML content from a web page.
from bs4 import BeautifulSoup

# Import the Tavily client used to run a search API query.
from tavily import TavilyClient

# Import the operating-system module to read environment variables.
import os

# Import Rich's print so output can be displayed in a styled console if desired.
from rich import print

# Import dotenv loader that reads key/value pairs from a .env file.
from dotenv import load_dotenv

import streamlit as st

# Load variables from a local .env file into the process environment.
load_dotenv()

# Function to get API key from Streamlit secrets or environment
def get_api_key(key_name):
    """Get API key from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (Streamlit Cloud)
        return st.secrets[key_name]
    except (KeyError, FileNotFoundError, AttributeError):
        # Fall back to environment variables (local .env)
        return os.getenv(key_name)

# Build a Tavily API client using the TAVILY_API_KEY from secrets or environment.
tavily = TavilyClient(api_key=get_api_key("TAVILY_API_KEY"))

# -----------------------------------------------------------------------------
# web_Search(query: str) -> str
# -----------------------------------------------------------------------------
# Purpose:
#   This function is registered as a LangChain tool so an agent can ask Tavily to
#   search the live web for recent information about a topic.
#
# Flow:
#   1. Print the search question for visibility during debugging.
#   2. Call Tavily's search API with a small max result limit.
#   3. Loop through the returned result objects.
#   4. Build a readable text block for each result with a title, URL, and snippet.
#   5. Join all result blocks into one final string to return to the caller.
# -----------------------------------------------------------------------------
@tool
def web_Search(query: str) -> str:
    """Search the public web for recent and reliable information about a topic."""
    print("query recived is ", query)
    response = tavily.search(query=query, max_results=3)

    result = []

    for r in response["results"]:
        result.append(
            f"Title: {r['title']} \nURL: {r['url']} \nSnippets: {r['content'][:300]} \n"
        )
    return "\n------\n".join(result)


# Execute the tool immediately with a sample question to test its output.
# print(web_Search.invoke("what is the recent news on pok    "))

# -----------------------------------------------------------------------------
# scrape_Url(url: str) -> str
# -----------------------------------------------------------------------------
# Purpose:
#   This function receives a URL and retrieves the public web page content using
#   a normal HTTP GET request, then extracts useful text from the HTML.
#
# Flow:
#   1. Send a GET request to the target page with a browser-like user-agent.
#   2. Parse the response with BeautifulSoup.
#   3. Remove noisy HTML sections such as scripts, styles, navigation, and footer.
#   4. Convert the remaining HTML into plain text.
#   5. Return a shortened preview of the extracted text (first 3000 chars).
#   6. If anything fails, return a safe error message instead of crashing.
# -----------------------------------------------------------------------------
@tool
def scrape_Url(url: str) -> str:
    """Scrape a webpage URL and return a cleaned text preview."""
    try:
        res = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"