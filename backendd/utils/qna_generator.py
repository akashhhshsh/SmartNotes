from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        # Initialize Ollama
        self.llm = OllamaLLM(
            model="mistral",
            base_url="http://localhost:11434",
            temperature=0.7,
            num_ctx=4096,
            top_k=10,
            repeat_penalty=1.1
        )
        
        # Enhanced prompt template
        self.prompt_template = PromptTemplate(
            template="""You are an expert educational assistant preparing students for exams. 
            Using the provided context, create a comprehensive and detailed answer.

            Context: {context}
            Question: {question}

            Please structure your response as follows:
            1. Main Concept: Provide a clear overview of the core idea
            2. Detailed Explanation: Break down the concept into digestible parts
            3. Key Features: List and explain important characteristics
            4. Examples/Applications: Provide relevant real-world examples
            5. Summary: Recap the most important points to remember

            Additional guidelines:
            - Use clear, academic language
            - Define technical terms
            - Include specific examples
            - Make connections between related concepts
            - Highlight exam-relevant points
            
            Detailed Answer:""",
            input_variables=["context", "question"]
        )
        
        # Initialize embeddings and vector store
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )

    def add_document(self, text: str):
        """Process and add document to vector store"""
        try:
            chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
            logger.info(f"Processing {len(chunks)} text chunks")
            self.vector_store.add_texts(chunks)
            logger.info("Successfully added chunks to vector store")
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise

    def generate_answer(self, question: str) -> str:
        """Generate comprehensive answer using RAG"""
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 5}
                ),
                chain_type_kwargs={
                    "prompt": self.prompt_template,
                    "verbose": True
                }
            )
            
            result = qa_chain.invoke({"query": question})
            return result.get("result")
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return None
