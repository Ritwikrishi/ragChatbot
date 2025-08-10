import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from pathlib import Path

from config import Config
from rag_system import RAGSystem
from vector_store import VectorStore
from ai_generator import AIGenerator
from session_manager import SessionManager
from document_processor import DocumentProcessor
from models import Course, Lesson, CourseChunk


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def test_config(temp_dir):
    """Create test configuration with temporary directories"""
    config = Config()
    config.vector_db_path = os.path.join(temp_dir, "test_chroma_db")
    config.chunk_size = 100
    config.chunk_overlap = 20
    config.max_conversation_history = 5
    return config


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing"""
    with patch('anthropic.Anthropic') as mock_client:
        # Mock the messages.create method
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_response.stop_reason = "end_turn"
        
        mock_instance.messages.create.return_value = mock_response
        
        yield mock_instance


@pytest.fixture
def sample_courses():
    """Create sample course data for testing"""
    lesson1 = Lesson(
        title="Introduction to Python",
        content="Python is a programming language. It is easy to learn.",
        lesson_number=1,
        metadata={"difficulty": "beginner"}
    )
    
    lesson2 = Lesson(
        title="Python Variables",
        content="Variables in Python are used to store data. You can create variables using assignment.",
        lesson_number=2,
        metadata={"difficulty": "beginner"}
    )
    
    course = Course(
        title="Python Basics",
        description="Learn the fundamentals of Python programming",
        lessons=[lesson1, lesson2],
        metadata={"category": "programming", "duration": "4 weeks"}
    )
    
    return [course]


@pytest.fixture
def sample_chunks(sample_courses):
    """Create sample course chunks for testing"""
    course = sample_courses[0]
    chunks = []
    
    chunk1 = CourseChunk(
        content="Python is a programming language. It is easy to learn.",
        course_title="Python Basics",
        lesson_title="Introduction to Python",
        lesson_number=1,
        chunk_index=0,
        metadata={"difficulty": "beginner", "category": "programming"}
    )
    
    chunk2 = CourseChunk(
        content="Variables in Python are used to store data. You can create variables using assignment.",
        course_title="Python Basics",
        lesson_title="Python Variables",
        lesson_number=2,
        chunk_index=0,
        metadata={"difficulty": "beginner", "category": "programming"}
    )
    
    return [chunk1, chunk2]


@pytest.fixture
def mock_vector_store(test_config, sample_chunks):
    """Mock vector store with sample data"""
    with patch('vector_store.VectorStore') as mock_vs:
        mock_instance = Mock()
        mock_vs.return_value = mock_instance
        
        # Mock search results
        mock_instance.search.return_value = sample_chunks[:1]  # Return first chunk
        mock_instance.get_all_chunks.return_value = sample_chunks
        mock_instance.add_chunks.return_value = None
        mock_instance.clear.return_value = None
        
        yield mock_instance


@pytest.fixture
def mock_ai_generator(mock_anthropic_client):
    """Mock AI generator with Anthropic client"""
    with patch('ai_generator.AIGenerator') as mock_ai:
        mock_instance = Mock()
        mock_ai.return_value = mock_instance
        
        # Mock generate response
        mock_instance.generate_response.return_value = (
            "This is a test response about Python programming.",
            ["Python Basics - Introduction to Python"]
        )
        
        yield mock_instance


@pytest.fixture
def mock_session_manager():
    """Mock session manager"""
    with patch('session_manager.SessionManager') as mock_sm:
        mock_instance = Mock()
        mock_sm.return_value = mock_instance
        
        mock_instance.create_session.return_value = "test-session-123"
        mock_instance.add_to_session.return_value = None
        mock_instance.get_session_history.return_value = []
        
        yield mock_instance


@pytest.fixture
def mock_document_processor():
    """Mock document processor"""
    with patch('document_processor.DocumentProcessor') as mock_dp:
        mock_instance = Mock()
        mock_dp.return_value = mock_instance
        
        mock_instance.process_course_folder.return_value = []
        
        yield mock_instance


@pytest.fixture
def mock_rag_system(test_config, mock_vector_store, mock_ai_generator, mock_session_manager):
    """Mock RAG system with all dependencies"""
    with patch('rag_system.RAGSystem') as mock_rag:
        mock_instance = Mock()
        mock_rag.return_value = mock_instance
        
        # Mock methods
        mock_instance.query.return_value = (
            "This is a test response about Python programming.",
            ["Python Basics - Introduction to Python"]
        )
        mock_instance.get_course_analytics.return_value = {
            "total_courses": 1,
            "course_titles": ["Python Basics"]
        }
        mock_instance.add_course_folder.return_value = (1, 2)  # 1 course, 2 chunks
        
        yield mock_instance


@pytest.fixture
def test_app_without_static():
    """Create test FastAPI app without static file mounting to avoid import issues"""
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from pydantic import BaseModel
    from typing import List, Optional
    
    # Create separate test app
    app = FastAPI(title="Test Course Materials RAG System")
    
    # Add middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Define models inline to avoid import issues
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None
    
    class QueryResponse(BaseModel):
        answer: str
        sources: List[str]
        session_id: str
    
    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]
    
    # Mock RAG system for testing
    mock_rag = Mock()
    mock_rag.query.return_value = (
        "This is a test response about Python programming.",
        ["Python Basics - Introduction to Python"]
    )
    mock_rag.get_course_analytics.return_value = {
        "total_courses": 1,
        "course_titles": ["Python Basics"]
    }
    mock_rag.session_manager.create_session.return_value = "test-session-123"
    
    # Define endpoints inline
    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag.session_manager.create_session()
            
            answer, sources = mock_rag.query(request.query, session_id)
            
            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = mock_rag.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/")
    async def root():
        return {"message": "Course Materials RAG System API"}
    
    return app


@pytest.fixture
def test_client(test_app_without_static):
    """Create test client for API testing"""
    return TestClient(test_app_without_static)


@pytest.fixture
def sample_query_request():
    """Sample query request for testing"""
    return {
        "query": "What is Python?",
        "session_id": "test-session-123"
    }


@pytest.fixture
def expected_query_response():
    """Expected query response for testing"""
    return {
        "answer": "This is a test response about Python programming.",
        "sources": ["Python Basics - Introduction to Python"],
        "session_id": "test-session-123"
    }


@pytest.fixture
def expected_course_stats():
    """Expected course statistics for testing"""
    return {
        "total_courses": 1,
        "course_titles": ["Python Basics"]
    }