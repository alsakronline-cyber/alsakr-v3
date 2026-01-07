import os
import logging
from typing import List, Dict, Optional
from haystack import Pipeline
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator  # We'll use this with custom Ollama URL
from haystack.document_stores.in_memory import InMemoryDocumentStore
# Note: For production with PgVector, we would use PgvectorDocumentStore.
# Since we haven't installed the specific driver in the environment yet, 
# I will use InMemoryDocumentStore for the initial "dry run" code to ensure it validates,
# but I will leave the Pgvector code commented out for the real deployment.

# from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
# from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever

logger = logging.getLogger(__name__)

class HaystackPipeline:
    def __init__(self):
        # Placeholder for PgVector Setup
        # self.document_store = PgvectorDocumentStore(
        #     connection_string=os.getenv("POSTGRES_CONN_STR"),
        #     table_name="haystack_docs",
        #     embedding_dimension=768
        # )
        
        self.document_store = InMemoryDocumentStore()
        self.template = """
        You are a helpful industrial AI assistant for Al Sakr Online.
        Answer the user's question based ONLY on the provided context.
        If the answer is not in the context, say "I don't have enough information in my database."

        Context:
        {% for doc in documents %}
            {{ doc.content }}
        {% endfor %}

        Question: {{ question }}

        Answer:
        """
        
        self.rag_pipeline = Pipeline()
        self.rag_pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=self.document_store))
        self.rag_pipeline.add_component("prompt_builder", PromptBuilder(template=self.template))
        # Pointing to Ollama
        self.rag_pipeline.add_component("llm", OpenAIGenerator(
            api_key="ollama",
            api_base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/v1",
            model="mistral"
        ))
        
        self.rag_pipeline.connect("retriever", "prompt_builder.documents")
        self.rag_pipeline.connect("prompt_builder", "llm")

    def query(self, question: str):
        result = self.rag_pipeline.run({
            "retriever": {"query": question},
            "prompt_builder": {"question": question}
        })
        return result["llm"]["replies"][0]

    def index_data(self, data: List[Dict]):
        from haystack import Document
        docs = [Document(content=d["content"], meta=d["meta"]) for d in data]
        self.document_store.write_documents(docs)
        return len(docs)
