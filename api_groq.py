import os
from dotenv import load_dotenv
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.tools import PythonAstREPLTool
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain_core.output_parsers import StrOutputParser
from app import retrive_data_from_redis

load_dotenv()


data_key = retrive_data_from_redis("data_key")
clustering_data = data_key['result_kmeans']
df = pd.DataFrame(data=clustering_data['data'],columns=clustering_data['header'])

groq_api_key = os.getenv('GROQ_KEY')


python_repl = PythonAstREPLTool(locals={"df": df},verbose=True)


llm = ChatGroq(
    model="llama3-70b-8192",
    api_key=groq_api_key,
    temperature=0.7
)

system_prompt = """
You are a data analyst AI. Your task is to analyze the provided DataFrame (`df`) and answer user questions.
Whenever possible, use Python code to analyze the data and provide the results in a clear and concise manner.
If the user asks for a visualization, provide the code to generate it.
"""

# Create the chat prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

tools = [python_repl]

# Bind the tools to the LLM
llm_with_tools = llm.bind_tools(tools, tool_choice=python_repl.name)

# Initialize the parser to extract tool output
parser = JsonOutputKeyToolsParser(key_name=python_repl.name, first_tool_only=True)

output_parser = StrOutputParser()

# Loop interaktif di terminal
if __name__ == "__main__":
    print("🤖: Hello! I am your data analyst AI. Ask me anything about the dataset.")
    while True:
        # Get user input
        query_string = input("\nYou: ")
        
        # Exit condition
        if query_string.lower() in ["exit", "quit"]:
            print("🤖: Goodbye!")
            break
        
        # Create the chain: prompt -> LLM with tools -> output parser
        print(f'output_parser : {output_parser}')
        chain = prompt | llm_with_tools | output_parser | python_repl
        
        # Invoke the chain with the user input
        try:
            response = chain.invoke({"input": query_string})
            python_code = response['query']
            print(f'python code : {python_code}')
            print(f"🤖: {response}")
        except Exception as e:
            print(f"🤖: Sorry, I encountered an error: {e}")