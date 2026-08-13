# Agentic AI Research Pipeline

This repository is a compact LangChain-based research automation project. The goal of the system is to accept a user-provided research topic, gather fresh web information, read one relevant page in more depth, generate a research-style report, and finally review that report through a critic prompt.

The project is intentionally structured around a simple workflow:

1. Use an LLM-powered search agent to discover information.
2. Use a reader agent and web scraper to extract deeper context.
3. Build a final research report from the collected evidence.
4. Ask a second LLM chain to critique the generated result.

This is a good example of an agentic research pipeline that mixes LLM reasoning with external tools.

## Activate evironment for local => .venv\Scripts\activate   

## Repository structure

The current project is made up of these main files:

- [app.py](app.py) provides the Streamlit-based web user interface for running the research workflow in a browser.
- [agents.py](agents.py) configures the LLM models, search agent, reader agent, writer chain, and critic chain.
- [tools.py](tools.py) provides the two custom LangChain tools used by the agents: web search and URL scraping.
- [pipeline.py](pipeline.py) orchestrates the whole workflow and stores the intermediate outputs in a shared state dictionary.
- [pyproject.toml](pyproject.toml) declares the project metadata and dependencies.
- [requirement.txt](requirement.txt) lists the requirements used by the environment.

## Streamlit UI

The repository now includes a Streamlit web UI implemented in [app.py](app.py). It gives the research pipeline a browser-based front end where a topic can be entered in the sidebar, the pipeline can be launched, and the run history and generated outputs are shown in tabs.

The UI is designed around the same internal flow as the pipeline:

- Search Agent finds public information
- Reader Agent selects and scrapes a relevant page
- Writer Chain creates the final report
- Critic Chain evaluates the report

### Run locally

Make sure the dependencies are installed and then start the app with:

```bash
streamlit run app.py
```

Once the app is running, open the local Streamlit URL in your browser and submit a research topic from the left-side control deck.

## How the system works

The flow is:

```text
Topic input
  -> Search Agent
  -> Search result stored in memory
  -> Reader / scraper Agent
  -> Scraped content stored in memory
  -> Writer chain builds report
  -> Critic chain reviews report
```

A user enters a topic. That topic is passed into the search agent, which uses a search tool to fetch external information. The search result is saved into a state object. The pipeline then asks the reader agent to inspect the result, pick a relevant URL, and fetch the article text. The scraped output is stored in the same state object. The writer chain combines the search and scraping outputs and creates a final report. Finally, the critic chain evaluates that report and returns feedback.

## File-by-file explanation

### agents.py

This file acts as the AI configuration and orchestration layer.

It imports the pieces needed to create LangChain prompt pipelines and agent abstractions:

- LangChain's `create_agent` helper
- `ChatPromptTemplate` for building prompts
- `StrOutputParser` for plain-text parsing at the end of a chain
- Gemini and Groq model adapters
- Custom tools exported from [tools.py](tools.py)

The file sets up two LLM models:

```python
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0)
llm2 = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
```

The repository currently uses two model objects:

- `llm` is the Gemini-backed model used for the search agent and reader agent.
- `llm2` is the Groq-backed model used for the critic stage.

The writer chain continues to use `llm` as the report-generation model.

#### build_Search_Agent()

This function returns a LangChain agent that is configured with the `web_Search` tool.

```python
def build_Search_Agent():
    return create_agent(model=llm, tools=[web_Search])
```

That search agent is designed to answer questions like “find recent and reliable information about this topic.”

#### build_Reader_Agent()

This function returns a second agent using the `scrape_Url` tool.

```python
def build_Reader_Agent():
    return create_agent(model=llm, tools=[scrape_Url])
```

The reader agent receives a search summary and is expected to choose the most useful URL and scrape it for more detail.

#### Writer Chain

The writer prompt is a `ChatPromptTemplate` that asks the language model for a research report in a defined structure:

- introduction
- key findings
- conclusion
- sources

The chain is built as:

```python
writer_Chain = writer_prompt | llm | StrOutputParser()
```

This means the prompt template is passed to the LLM and the final answer is converted into a plain string.

#### Critic Chain

The critic prompt asks the LLM to evaluate the already generated report from a quality and evidence perspective.

The current project wiring uses the Groq model (`llm2`) for that stage:

```python
critic_Chain = critics_prompt | llm2 | StrOutputParser()
```

That chain returns the reviewer-style summary and verdict using the Groq LLM runtime instead of the Gemini writer model.

## tools.py

This file is the “external action layer” of the project. It contains the tool functions that the agents can call.

### web_Search

```python
@tool
def web_Search(query: str) -> str:
    """Search the public web for recent and reliable information about a topic."""
```

The `web_Search` method is registered as a LangChain tool. It uses Tavily search to query the web for recent information about a given topic. The returned result set is converted into a readable string that includes:

- article title
- article URL
- content snippet

This becomes the raw input for the first research stage.

### scrape_Url

```python
@tool
def scrape_Url(url: str) -> str:
    """Scrape a webpage URL and return a cleaned text preview."""
```

This tool runs an HTTP GET request against a website and extracts readable text using BeautifulSoup. It removes page noise such as scripts, styles, navigation blocks, and footers, then returns a text preview of the page content for the downstream writer agent.

If the HTTP request fails or the page cannot be parsed, it returns a safe error message.

## pipeline.py

This file is the main execution pipeline. It coordinates the entire research lifecycle and passes data across several stages.

The main function is:

```python
def run_research_pipeline(topic: str) -> dict:
```

That function creates a local `state` dictionary to keep all intermediate and final artifacts.

### Search stage

The first stage creates a search agent and asks it for reliable information.

```python
search_Agent = build_Search_Agent()
search_result = search_Agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": f"Find recent and reliable information about :{topic}"
        }
    ]
})
```

The result is read from the message list and stored as:

```python
state["search_result"]
```

### Reader / scraping stage

The second stage creates a reader agent and passes the first search summary to it. The prompt asks it to review the search content, select the most relevant URL, and scrape the page.

```python
reader_agent = build_Reader_Agent()
reader_result = reader_agent.invoke({
    "messages": [{
        "role": "user",
        "content": (
            f"Based on the following search result about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Result:\n{state['search_result'][:800]}"
        ),
    }]
})
```

The final scraped result is stored as:

```python
state["scrape_result"]
```

### Report-generation stage

The search output and scraped output are joined into a single research block:

```python
research_result = (
    f"SEARCH RESULTS: \n {state['search_result']} \n\n"
    f"DETAILED SCRAPED CONTENTS: \n {state['scrape_result']}"
)
```

That combined research knowledge is passed into `writer_Chain.invoke(...)`:

```python
state["report"] = writer_Chain.invoke({
    "topic": topic,
    "research": research_result
})
```

The returned output becomes the final polished report.

### Critic stage

The report string is then passed to the critic chain:

```python
state["feedback"] = critic_Chain.invoke({
    "report": state["report"]
})
```

The feedback returned by the critic is saved to `state["feedback"]` and printed for the user.

### Entry point

The script uses the standard Python main guard:

```python
if __name__ == "__main__":
    topic = input("\n Enter a research topic :")
    run_research_pipeline(topic=topic)
```

That block only runs when the file is executed directly as a script, not when it is imported by another file.

## Environment and runtime notes

The project expects a `.env` file with provider credentials, especially a Tavily API key:

```text
TAVILY_API_KEY=<your-key>
```

The Google Gemini and Groq integrations also depend on environment configuration and provider credentials being available to the LangChain adapters.

## Running the project

You can run the pipeline from the repository root using `uv`:

```bash
uv run python pipeline.py
```

The program prompts the user for a topic and then performs the full research pipeline.

## Dependencies

The runtime package set is defined in [pyproject.toml](pyproject.toml) and includes:

- LangChain and LangChain Core
- Gemini integration via `langchain-google-genai`
- Groq integration via `langchain-groq`
- Tavily API client
- Markdown-friendly and prompt generation tooling
- BeautifulSoup / requests for scraping
- Python dotenv for environment variables

## Summary

This repository demonstrates a practical multi-agent AI research flow. The value comes from combining external searching, page extraction, structured report generation, and LLM-based evaluation in a single pipeline.

## Project Deployed using streamlit cloud

 - url : https://ai-agent-6tzvjafpl4dsy8et3vg9au.streamlit.app/
