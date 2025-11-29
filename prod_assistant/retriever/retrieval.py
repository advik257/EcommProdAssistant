import os
from langchain_astradb import AstraDBVectorStore
from typing import List
from langchain_core.documents import Document
from prod_assistant.utils.config_loader import load_config
from prod_assistant.utils.model_loader import ModelLoader
from dotenv import load_dotenv

class Retriever:
    
    """Base class for all retrievers."""
    
    def __init__(self):
        pass
    
    def _load_env_varaibles(self):
        pass
    
    
    def load_retriever(self):
        pass
    
    
    
    def call_retriever(self):
        pass
    

if __name__ == "__main__":
    retriever = Retriever()
    
    user_query ="can you suggest good budget loptop?"
    results = retriever.call_retriever(user_query)
    for doc in results:
        print(doc.page_content)
        print("-----")
        print(doc.metadata)
    