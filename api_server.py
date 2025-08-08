#!/usr/bin/env python3
"""
FastAPI Server for SmartDoctors RAG System
Provides REST API endpoints for doctor recommendations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn
from rag_system import SmartDoctorsRAG
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize data if needed
def initialize_data():
    """Initialize doctors data and embeddings if they don't exist"""
    import subprocess
    import sys
    
    # Check if doctors_data.json exists
    if not os.path.exists("doctors_data.json"):
        print("Generating doctors data...")
        subprocess.run([sys.executable, "generate_doctor_data.py"], check=True)
    
    # Check if ChromaDB is initialized
    try:
        import chromadb
        from chromadb.config import Settings
        client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        collection = client.get_collection(name="doctors")
        print(f"ChromaDB collection found with {collection.count()} items")
    except Exception as e:
        print(f"Initializing ChromaDB: {e}")
        subprocess.run([sys.executable, "create_embeddings.py"], check=True)

# Initialize data on startup
initialize_data()

# Initialize FastAPI app
app = FastAPI(
    title="SmartDoctors API",
    description="AI-powered doctor recommendation system",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
use_llm = os.getenv("OPENAI_API_KEY") is not None
rag_system = SmartDoctorsRAG(use_openai=use_llm)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for request/response
class PatientQuery(BaseModel):
    query: str = Field(..., description="Patient's symptoms or medical concern")
    location: Optional[str] = Field(None, description="Preferred location (e.g., 'New York, NY')")
    specialty: Optional[str] = Field(None, description="Preferred specialty filter")
    n_results: int = Field(5, description="Number of doctors to retrieve", ge=1, le=20)

class DoctorInfo(BaseModel):
    doctor_id: str
    name: str
    specialty: str
    sub_specialty: str
    location: str
    hospital: str
    experience: int
    languages: str
    surgeries_summary: str
    expertise: str
    similarity_score: float

class RecommendationResponse(BaseModel):
    success: bool
    recommendation: Optional[Dict[str, Any]]
    message: Optional[str] = None
    timestamp: str

class HealthCheck(BaseModel):
    status: str
    llm_enabled: bool
    database_connected: bool
    message: str

# API Endpoints
@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML"""
    return FileResponse('static/index.html')

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "llm_enabled": use_llm,
        "database_connected": True,
        "message": "SmartDoctors API is running"
    }

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(patient_query: PatientQuery):
    """
    Get doctor recommendation based on patient query
    
    This endpoint uses both vector search and LLM to provide
    intelligent doctor recommendations.
    """
    try:
        result = rag_system.process_patient_query(
            query=patient_query.query,
            location=patient_query.location,
            specialty=patient_query.specialty,
            n_results=patient_query.n_results
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_doctors(patient_query: PatientQuery):
    """
    Search for doctors without LLM recommendation
    
    This endpoint only performs vector search and returns
    ranked results without generating explanations.
    """
    try:
        results = rag_system.search_doctors(
            query=patient_query.query,
            location_filter=patient_query.location,
            specialty_filter=patient_query.specialty,
            n_results=patient_query.n_results
        )
        
        return {
            "success": True,
            "results": [r.to_dict() for r in results],
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/locations")
async def get_available_locations():
    """Get list of available locations"""
    # In a real implementation, you'd query this from the database
    locations = [
        "New York, NY",
        "Los Angeles, CA",
        "Chicago, IL",
        "Houston, TX",
        "Boston, MA",
        "Philadelphia, PA",
        "Seattle, WA",
        "San Francisco, CA",
        "Atlanta, GA",
        "Miami, FL"
    ]
    return {"locations": locations}

@app.get("/specialties")
async def get_available_specialties():
    """Get list of available specialties"""
    # In a real implementation, you'd query this from the database
    specialties = [
        "Cardiology",
        "Neurosurgery",
        "Oncology",
        "Orthopedic Surgery",
        "Pediatrics",
        "Gastroenterology",
        "Urology",
        "Dermatology",
        "Neurology",
        "Obstetrics and Gynecology"
    ]
    return {"specialties": specialties}

# Example usage endpoint with pre-defined queries
@app.get("/examples")
async def get_example_queries():
    """Get example patient queries for testing"""
    examples = [
        {
            "query": "I've been having severe chest pain and shortness of breath",
            "location": "New York, NY",
            "description": "Cardiac symptoms"
        },
        {
            "query": "My child has recurring ear infections and hearing problems",
            "location": "Boston, MA",
            "description": "Pediatric ENT issue"
        },
        {
            "query": "I need help with chronic back pain that radiates down my leg",
            "location": None,
            "description": "Neurological/Orthopedic issue"
        },
        {
            "query": "Looking for a dermatologist for severe acne treatment",
            "location": "Los Angeles, CA",
            "description": "Dermatological issue"
        },
        {
            "query": "Need oncologist for breast cancer second opinion",
            "location": "Houston, TX",
            "description": "Oncology consultation"
        }
    ]
    return {"examples": examples}

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("PORT", 8000))
    
    print(f"\n{'='*50}")
    print(f"Starting SmartDoctors API Server")
    print(f"{'='*50}")
    print(f"LLM Features: {'Enabled' if use_llm else 'Disabled (Set OPENAI_API_KEY to enable)'}")
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"{'='*50}\n")
    
    # Check if running in Docker
    is_docker = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=not is_docker  # Disable reload in Docker
    )