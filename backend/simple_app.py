"""
Simplified version of the RAG app that works without ML dependencies
This version provides a basic chat interface with Anthropic Claude
"""
import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Simple RAG Chatbot", description="Basic chat interface with Claude")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: list = []
    session_id: str = "default"

class CourseStats(BaseModel):
    total_courses: int = 0
    course_titles: list = []

# Simple session storage (in production, use a database)
sessions = {}

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Process a query and return response"""
    try:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="Anthropic API key not configured. Please add ANTHROPIC_API_KEY to your .env file."
            )
        
        # Create a session ID if not provided
        session_id = request.session_id or "default"
        
        # Get conversation history
        history = sessions.get(session_id, [])
        
        # Build the prompt with context
        system_prompt = """You are a helpful AI assistant. You can answer questions about various topics. 
        Since the full RAG system is not yet set up, you should use your general knowledge to provide helpful responses.
        
        Note: The vector search functionality is not available yet, so you're responding based on your training data."""
        
        # Build conversation context
        messages = []
        for exchange in history[-3:]:  # Keep last 3 exchanges
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["assistant"]})
        
        # Add current query
        messages.append({"role": "user", "content": request.query})
        
        # Call Claude
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=800,
            temperature=0,
            system=system_prompt,
            messages=messages
        )
        
        answer = response.content[0].text
        
        # Store in session
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append({
            "user": request.query,
            "assistant": answer
        })
        
        return QueryResponse(
            answer=answer,
            sources=["General AI Knowledge (RAG system not fully initialized)"],
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courses", response_model=CourseStats)
async def get_course_stats():
    """Get course statistics (placeholder)"""
    return CourseStats(
        total_courses=0,
        course_titles=["Full RAG system not initialized - install ChromaDB and sentence-transformers to enable course search"]
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key_configured = bool(os.getenv("ANTHROPIC_API_KEY"))
    return {
        "status": "healthy",
        "anthropic_api_configured": api_key_configured,
        "mode": "simplified"
    }

# Serve static files for the frontend
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)