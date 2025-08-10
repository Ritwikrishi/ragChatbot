# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- **Start server**: `./run.sh` (recommended) or `cd backend && uv run uvicorn app:app --reload --port 8000`
- **Install dependencies**: `uv sync`
- **Access points**: 
  - Web interface: http://localhost:8000
  - API docs: http://localhost:8000/docs

### Environment Setup
- Copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY`
- Requires Python 3.13+ and uv package manager

### Code Quality & Development
- **Format code**: `./format.sh` - Runs isort, black, and flake8
- **Lint only**: `./lint.sh` - Runs flake8 and mypy type checking  
- **Quality checks**: `./check.sh` - Runs all checks without auto-fixing
- **Manual commands**:
  - `uv run black backend/ main.py` - Format with Black
  - `uv run isort backend/ main.py` - Sort imports
  - `uv run flake8 backend/ main.py` - Lint with flake8
  - `uv run mypy backend/ main.py` - Type checking with mypy

**Quality Tools Configuration:**
- Black: Line length 88, Python 3.9+ compatibility
- isort: Black-compatible profile
- flake8: 88 char line limit, ignores E203/W503/E501
- mypy: Strict typing enabled

## Architecture Overview

This is a Retrieval-Augmented Generation (RAG) system for querying course materials with the following key components:

### Core System Architecture
- **RAGSystem** (`backend/rag_system.py`): Main orchestrator that coordinates all components
- **VectorStore** (`backend/vector_store.py`): ChromaDB-based vector storage using SentenceTransformer embeddings
- **AIGenerator** (`backend/ai_generator.py`): Anthropic Claude integration with tool-based search capabilities
- **DocumentProcessor** (`backend/document_processor.py`): Processes course documents into structured chunks
- **SessionManager** (`backend/session_manager.py`): Manages conversation history and sessions

### Data Models
- **Course**: Represents complete courses with lessons and metadata
- **CourseChunk**: Text chunks for vector storage with course/lesson context
- **Lesson**: Individual lessons within courses

### API Structure
- **FastAPI app** (`backend/app.py`) with CORS and static file serving
- **Key endpoints**:
  - `POST /api/query`: Process user queries with RAG
  - `GET /api/courses`: Get course statistics
- **Frontend**: Vanilla HTML/CSS/JS in `frontend/` directory

### Search and Tool System
- **ToolManager** (`backend/search_tools.py`): Manages available search tools
- **CourseSearchTool**: Semantic search through course content using ChromaDB
- Claude uses tools to search course content rather than direct vector retrieval

### Configuration
- All settings in `backend/config.py` with environment variable support
- Key settings: chunk size (800), overlap (100), embedding model (all-MiniLM-L6-v2)
- Claude model: claude-sonnet-4-20250514

### Document Processing Flow
1. Documents added from `docs/` folder on startup
2. Content processed into structured Course objects with lessons
3. Text chunked and stored in ChromaDB with metadata
4. Search tools provide semantic retrieval for AI responses

### Session Management
- Maintains conversation context with configurable history length
- Session-based queries for contextual responses