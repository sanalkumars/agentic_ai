# This file will contains two agents one using the web_search tool and the other uses
# the web scraper tool

# create_react_agent is no longer used in the latest version of langchain, so we will use create_agent instead

import os
import streamlit as st
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 2. Gemini (Google GenAI) Imports
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 3. Groq Import
from langchain_groq import ChatGroq
# import tools
from tools import web_Search, scrape_Url
from dotenv import load_dotenv
load_dotenv()

# Function to get API keys from Streamlit secrets or environment
def get_api_key(key_name):
    """Get API key from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (Streamlit Cloud)
        return st.secrets[key_name]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variables (local .env)
        return os.getenv(key_name)

# Initialize models with API keys from secrets or env
# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash", 
#     temperature=0,
#     google_api_key=get_api_key("GEMINI_API_KEY")
# )

llm2 = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0,
    groq_api_key=get_api_key("GROQ_API_KEY")
)

# 1st Research Agent
def build_Search_Agent():
    return create_agent(
        model = llm2,
        tools = [ web_Search ]
    )
# 2nd Agent(Reader Agent)
def build_Reader_Agent():
    return create_agent(
        model = llm2,
        tools = [ scrape_Url ]
    )


# writer chain( reserch chain)
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful report."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list minimum 3  URLs found in the research)

Be detailed, factual and professional."""),
])

# we create a writer chain

writer_Chain = writer_prompt | llm2 | StrOutputParser()

# critics prompt
critics_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research critic and reviewer. Evaluate research reports for accuracy, structure, clarity, and depth."),
    ("human", """Evaluate the following research report based on the provided topic and research data.



Generated Report:
{report}

Evaluation Criteria:
1. Topic Relevance & Focus (0-25 points)
2. Quality & Depth of Key Findings (At least 3 well-explained points) (0-25 points)
3. Structure & Formatting Adherence (Introduction, Key Findings, Conclusion, Sources) (0-25 points)
4. Factuality & Source Usage (0-25 points)

Please provide your review in the following format:
- Overall Score: [Total / 100]
- Strengths: [Brief summary]
- Weaknesses / Missing Details: [Brief summary]
- Actionable Recommendations: [Specific suggestions for improvement]
- Final Verdict: [Pass / Needs Revision]"""),
])

# we will user the groq llm(llm2) for criticising the final report
critic_Chain = critics_prompt | llm2 | StrOutputParser()