"""
Exemplo de uso das bibliotecas instaladas
"""

# LangChain imports
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# LangChain Groq
try:
    from langchain_groq import ChatGroq
except ImportError:
    print("LangChain Groq não disponível")

# LangChain Community
from langchain_community.llms import HuggingFacePipeline
from langchain_community.document_loaders import TextLoader

# YouTube Transcript API
from youtube_transcript_api import YouTubeTranscriptApi

# PyPDF
from pypdf import PdfReader

# Exemplo de uso básico
if __name__ == "__main__":
    print("Bibliotecas importadas com sucesso!")
    
    # Exemplo: Leitura de PDF
    # reader = PdfReader("exemplo.pdf")
    # for page in reader.pages:
    #     print(page.extract_text())
    
    # Exemplo: Transcript do YouTube
    # transcript = YouTubeTranscriptApi.get_transcript("VIDEO_ID")

