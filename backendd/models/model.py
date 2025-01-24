from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import uuid
import logging

from utils.pdf_reader import extract_text_from_pdf
from utils.qna_generator import RAGSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PDF Q&A Generator",
    description="RAG-powered PDF Question Answering System"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = RAGSystem()

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Welcome to PDF Q&A Generator",
        "endpoints": {
            "upload_pdf": "/upload-pdf",
            "generate_answers": "/generate-answers",
            "documentation": "/docs"
        }
    }

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        filename = f"{uuid.uuid4()}.pdf"
        file_path = os.path.join("uploads", filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(file_path)
        
        if not pdf_text:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Unable to extract text from PDF")
        
        # Add document to RAG system
        rag_system.add_document(pdf_text)
        
        logger.info(f"Successfully processed PDF: {filename}")
        
        return {
            "status": "success",
            "filename": filename,
            "text_length": len(pdf_text)
        }
    
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-answers")
async def generate_answers(question: str):
    try:
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        answer = rag_system.generate_answer(question)
        return {"answer": answer}
    
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
