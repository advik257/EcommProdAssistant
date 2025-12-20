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
        self.model_loader=ModelLoader()
        self._load_env_varaibles()
        self.config=load_config()
        self.vector_store = None
        self.retriever = None
    
    def _load_env_varaibles(self):
        
        load_dotenv()
        
        required_vars = ["COHERE_API_KEY", "ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "ASTRA_DB_KEYSPACE"]
        
        missing_vars = [var for var in required_vars if os.getenv(var) is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE")
    
    
    def load_retriever(self):
        """
        Load the retriever from AstraDB vector store.
        """
        if not self.vector_store:
            
            collection_name=self.config["astra_db"]["collection_name"]
            
            self.vector_store = AstraDBVectorStore(
                embedding= self.model_loader.load_embeddings(),
                collection_name=collection_name,
                api_endpoint=self.db_api_endpoint,
                token=self.db_application_token,
                namespace=self.db_keyspace
            )        
            
            top_k = self.config["retriever"]["top_k"]
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})
            
            return self.retriever
        
    
    def call_retriever(self, query):
        
        """ call the retriever to get relevant documents."""
        
        retriever = self.load_retriever()
        output = retriever.invoke(query)
        
        return output
    

if __name__ == "__main__":
    retriever = Retriever()
    
    user_query ="can you suggest good budget phones?"
    results = retriever.call_retriever(user_query)
    for doc in results:
        print(doc.page_content)
        print("-----")
        print(doc.metadata)
    