

# Agentic AI Learning Project

This repository is a learning project for building agentic AI workflows with Python, LangChain, LLM providers, vector search, and local experimentation.

## Project Structure

- `main.py` is the main entry point for the project.
- `first_llm_calling/sample_llm_calling.py` shows direct LLM calls using Google and Groq models.
- `lanchain-course/lang-chain-course.py` shows a LangChain agent that uses an LLM model and a custom tool.
- `vector_db/main.py` demonstrates a local ChromaDB vector database with sentence embeddings.

## Local Setup

Use the virtual environment from the project root:

```bash
.venv\Scripts\activate
```

Or, if using `uv`:

```bash
uv run python main.py
```

Replace `main.py` with the script you want to run.

## Dependencies from `requirement.txt`

The dependencies in the project are as follows:

| Library | Version / Package | Usage in this project |
| --- | --- | --- |
| `langchain` | `langchain[google-genai]>=0.3.0` | Core orchestration library for building LLM-powered applications, agents, prompts, and model integrations. |
| `langchain-core` | `>=1.0.0` | Shared core abstractions such as message types, chat model interfaces, and LangChain runtime classes. |
| `langchain-google-genai` | `>=4.2.2` | Google Generative AI integration for calling Gemini models from the LangChain stack. |
| `langchain-groq` | `>=0.3.0` | Groq provider integration for ChatGroq models such as `llama-3.1-8b-instant`. |
| `python-dotenv` | `>=1.2.2` | Loads environment variables from a `.env` file so API keys and model configuration can stay out of source code. |
| `streamlit` | `>=1.57.0` | Used for creating UI-based AI applications or dashboards. |
| `ipykernel` | `>=7.2.0` | Jupyter kernel support for interactive notebooks in VS Code or Python environments. |
| `notebook` | `>=7.5.6` | Notebook runtime for exploration and visual experiments. |
| `chromadb` | `chromadb` | Local vector database used to store and query embeddings. The project uses it in the vector DB example. |
| `sentence-transformers` | `>=2.2.2` | Embedding model provider used to create text embeddings for semantic search with ChromaDB. |
| `pandas` | `pandas` | Data analysis and manipulation library for tabular or experiment data workflows. |
| `tavily-python` | `>=0.7.27` | Tavily API client for web search and retrieval workflows. |
| `beautifulsoup4` | `>=4.15.0` | HTML parsing library for scraping and cleaning web page content. |
| `requests` | `>=2.34.2` | Makes HTTP requests to web services, APIs, or page fetches. |
| `langchain-community` | `>=0.4.2` | Community integrations and third-party components that extend LangChain components. |

## Usage Notes

### LLM Integration

The project uses LangChain model wrappers to call LLM providers:

- `ChatGoogleGenerativeAI` is used for Google Gemini access in the LLM calling example.
- `ChatGroq` is used to call Groq-hosted models such as Llama.
- `init_chat_model` and `create_agent` show LangChain’s higher-level abstraction for agentic model workflows.

### Environment Configuration

The project uses `.env` files via `python-dotenv` so credentials and API endpoints can be configured outside code.

### Vector Search

The project uses ChromaDB together with `SentenceTransformerEmbeddingFunction`, which allows storing text documents and running similarity searches against them.

### Web Retrieval

The web-related stack (`tavily-python`, `beautifulsoup4`, and `requests`) supports search, fetching, and HTML parsing for external knowledge retrieval.

### Data Analysis

`pandas` is included for tabular data operations and analysis-heavy tasks that may be added later in the learning workflow.

## Recommended Workflow

1. Activate the virtual environment.
2. Load model credentials with environment variables.
3. Run the examples from the folders that align with the lesson.
4. Keep the dependency list synchronized with `requirement.txt` and `pyproject.toml`.