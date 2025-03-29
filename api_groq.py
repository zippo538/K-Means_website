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

data = df.iloc[:,4:]
delete_col = ['Status','Gel','Jumlah absen TWK','Jumlah absen TIU','Jumlah absen TKP','cluster']
data = data.drop(delete_col, axis=1)
tryout_columns = data.columns.values.tolist()
cluster_stats = df.groupby('cluster').agg({
        'id user': 'count',
        tryout_columns[-1]: 'mean'
    }).to_string()
print(cluster_stats)

groq_api_key = os.getenv('GROQ_KEY')


python_repl = PythonAstREPLTool(locals={"df": df['cluster'].value_counts()},verbose=True)


llm = ChatGroq(
        model="llama3-70b-8192",
        api_key=groq_api_key,
        temperature=0.6
    )

system_prompt = f"""Buat laporan untuk guru dengan format markdown yang mencakup:
        1. Tabel perbandingan antar cluster
        2. Karakteristik unik tiap cluster
        3. Rekomendasi strategi mengajar
        4. Action plan spesifik
        
        Gunakan data berikut:
        {cluster_stats}
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
        report = llm.invoke(system_prompt)
        with open('rekomendasi_guru.md', 'w') as f:
            f.write(report.content)
        # print("🤖: Hello! I am your data analyst AI. Ask me anything about the dataset.")
        # while True:
        #     # Get user input
        #     query_string = input("\nYou: ")
            
        #     # Exit condition
        #     if query_string.lower() in ["exit", "quit"]:
        #         print("🤖: Goodbye!")
        #         break
            
        #     # Create the chain: prompt -> LLM with tools -> output parser
        #     print(f'output_parser : {output_parser}')
        #     chain = prompt | llm_with_tools | parser 
            
        #     questions = [
        #     "Apa karakteristik masing-masing cluster berdasarkan fitur numerik?",
        #     "Cluster mana yang memiliki nilai rata-rata tertinggi untuk kolom X?",
        #     "Buat ringkasan statistik per cluster"
        #     ]
            
        #     # Invoke the chain with the user input
        #     try:
        #         for q in questions:
        #             print(f"\n🔍 Pertanyaan: {q}")
        #             response = chain.invoke({"input": q})
        #             print(f"🤖 Jawaban:\n{response}")
        #     except Exception as e:
        #         print(f"🤖: Sorry, I encountered an error: {e}")