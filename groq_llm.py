from langchain.llms.base import LLM
from groq import Groq
from langchain_groq import ChatGroq
from pydantic import Field

class GroqLLM(LLM):
    model_name: str = Field(default="llama3-70b-8192")  # Deklarasikan model_name sebagai Field
    api_key: str  # Tambahkan api_key sebagai atribut yang diperlukan

    def __init__(self, api_key: str, model_name: str = "llama3-70b-8192"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = ChatGroq(api_key=api_key,model=model_name)  # Inisialisasi klien Groq
        super().__init__()

    def _call(self, prompt: str, stop=None) -> str:
        # Kirim prompt ke model Groq
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model_name,
        )
        # Ambil konten dari respons
        return response.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        return "groq"