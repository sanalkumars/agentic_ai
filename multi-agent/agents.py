# This file will contains two agents one using the web_search tool and the other uses
# the web scraper tool

# create_react_agent is no longer used in the latest version of langchain, so we will use create_agent instead

from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 2. Gemini (Google GenAI) Imports
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 3. Groq Import
from langchain_groq import ChatGroq
# import tools
from tools import web_Search, scrape_Url
from dotenv import load_dotenv
load_dotenv()

# models
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0)

llm2 = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# 1st Research Agent
def build_Search_Agent():
    return create_agent(
        model = llm,
        tools = [ web_Search ]
    )
# 2nd Agent(Reader Agent)
def build_Reader_Agent():
    return create_agent(
        model = llm,
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

writer_Chain = writer_prompt | llm | StrOutputParser()

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

critic_Chain = critics_prompt | llm | StrOutputParser()