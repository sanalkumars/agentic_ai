from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

load_dotenv()

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# Initialize the model explicitly with the Google GenAI provider
model = init_chat_model("gemini-3.5-flash", model_provider="google_genai")

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
)

print(result["messages"][-1].content)