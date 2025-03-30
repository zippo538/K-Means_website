import os
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.tools import PythonAstREPLTool
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain_core.output_parsers import StrOutputParser
from services.redis_service import RedisService


class ApiGroq : 
    def __init__(self,api_key : str,model_name : str = 'llama3-70b-8192', temperature : float = 0.6):
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        
    
    def recomendation(self,key_redis : str,key_data : str,delete_columns = None) : 
        data_key = RedisService.get_data(key=key_redis)
        clustering_data = data_key[key_data]
        df = pd.DataFrame(data=clustering_data['data'],columns=clustering_data['header'])

        data = df.iloc[:,4:]
        delete_columns = ['Status','Gel','Jumlah absen TWK','Jumlah absen TIU','Jumlah absen TKP','cluster']
        data = data.drop(delete_columns, axis=1)
        value = data.columns.values.tolist()

        cluster_stats = df.groupby('cluster').agg({
            'id user': 'count',
            value[-1]: 'mean'
        }).to_string()

        llm = ChatGroq(
            model=self.model_name,
            api_key=self.api_key,
            temperature=self.temperature,
        )

        system_prompt = f"""Buat laporan untuk guru dengan format markdown yang mencakup:
            1. Tabel perbandingan antar cluster
            2. Karakteristik unik tiap cluster
            3. Rekomendasi strategi mengajar
            4. Action plan spesifik
            
            Gunakan data berikut:
            {cluster_stats}
            """
      

        report = llm.invoke(system_prompt)
        with open('rekomendasi_guru.md', 'w') as f:
            return f.write(report.content)
