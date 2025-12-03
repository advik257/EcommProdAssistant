import os
from langchain_astradb import AstraDBVectorStore
from typing import List
from langchain_core.documents import Document
from prod_assistant.utils.config_loader import load_config
from prod_assistant.utils.model_loader import ModelLoader
from dotenv import load_dotenv
from prod_assistant.evaluation.ragas_eval import evaluate_context_precision, evaluate_response_relevancy



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
    
   
    
    user_query ="can you suggest good budget phones?"
    
    retriever = Retriever()
    
    retriever_docs = retriever.call_retriever(user_query)
    print(f"Retrieved {len(retriever_docs)} documents.")
    
    # def _format_retrieved_docs(doc_or_tuple) -> str:
    #     # If it's a tuple, take the first element (the Document)
    #     if isinstance(doc_or_tuple, tuple):
    #         doc = doc_or_tuple[0]
    #     else:
    #         doc = doc_or_tuple

    #     meta = getattr(doc, "metadata", {}) or {}
    #     formatted = (
    #         f"Title: {meta.get('product_title', 'N/A')}\n"
    #         f"Price: {meta.get('price', 'N/A')}\n"
    #         f"Rating: {meta.get('rating', 'N/A')}\n"
    #         f"Reviews: {getattr(doc, 'page_content', '').strip()}\n"
    #     )
    #     return formatted
    
    # retrieved_context = [_format_retrieved_docs(doc) for doc in retriever_docs]
    
    # # just test the pipeline
    
    response ="IPhone 16 plus , Iphone 15 pro max are good budget phones with great features and performance."
    
    # context_score = evaluate_context_precision(user_query,response ,retriever_docs)
    # relevancy_score = evaluate_response_relevancy(user_query,response, retriever_docs)
    
    # print("\n Evaluating Context Metrics:")
    # print("---------------------------")
    # print("\n Context Precision Score:", context_score)
    # print("\n Evaluaate Relevancy Score:", relevancy_score)
    
    # for idx , doc in enumerate(retrieved_context):
    #     print(f"Document {idx+1}:")
    #     print(doc.page_content)
    #     print("Metadata:", doc.metadata)
    #     print("-----")
    