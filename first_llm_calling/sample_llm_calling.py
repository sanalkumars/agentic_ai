from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


load_dotenv()

# we create the llm 

# llm = ChatGoogleGenerativeAI( model = "gemini-3.5-flash",temperature=0)

llm2 = ChatGroq(model="llama-3.1-8b-instant" )

# response = llm.invoke("How many moons does mars have")
# print( "response from llm", response.text)

# # if u want the answer to be structured/systematic output 

# res = llm.invoke([
#     ["system","The answer should be simple and not more that 2 line "],
#     ["human", " Explain Internet in simple terms "]
# ])

# print("second response",res.text)

first_prompt = "Your are a football analyser , i want u to analyse how good cristiano ronaldo is and provide a summary"

res2 = llm2.invoke(first_prompt)

# print("grok response",res2.text)

final_prompt = " Based on the res2 rate critiano is he the goat "

response = llm2.invoke(final_prompt)
print("final response",response.text)