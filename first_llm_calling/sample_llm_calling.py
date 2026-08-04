from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

# we create the llm 

llm = ChatGoogleGenerativeAI( model = "gemini-3.5-flash")

response = llm.invoke("How many moons does mars have")
print( "response from llm", response.text)

# if u want the answer to be structured/systematic output 

res = llm.invoke([
    ["system","The answer should be simple and not more that 2 line "],
    ["human", " Explain Internet in simple terms "]
])

print("second response",res.text)