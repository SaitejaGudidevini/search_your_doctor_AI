#!/usr/bin/env python3
"""
RAG System for SmartDoctors
Combines vector search with LLM-powered response generation
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "doctors"

@dataclass
class SearchResult:
    """Represents a doctor search result"""
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doctor_id": self.doctor_id,
            "name": self.name,
            "specialty": self.specialty,
            "sub_specialty": self.sub_specialty,
            "location": self.location,
            "hospital": self.hospital,
            "experience": self.experience,
            "languages": self.languages,
            "surgeries_summary": self.surgeries_summary,
            "expertise": self.expertise,
            "similarity_score": self.similarity_score
        }

class SmartDoctorsRAG:
    def __init__(self, use_openai: bool = True):
        """Initialize the RAG system"""
        print("Initializing SmartDoctors RAG System...")
        
        # Load embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)
        
        # Initialize LLM
        self.use_openai = use_openai
        if use_openai:
            # Make sure to set OPENAI_API_KEY in your .env file
            self.llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model_name = "gpt-3.5-turbo"  # or "gpt-4" for better quality
        else:
            # For now, we'll just use OpenAI. You can add other LLMs here
            print("Note: Currently only OpenAI is supported. Set use_openai=True")
    
    def search_doctors(
        self, 
        query: str, 
        location_filter: Optional[str] = None,
        specialty_filter: Optional[str] = None,
        n_results: int = 5
    ) -> List[SearchResult]:
        """
        Search for doctors based on patient query
        
        Args:
            query: Patient's problem description
            location_filter: Optional location filter (e.g., "New York, NY")
            specialty_filter: Optional specialty filter (e.g., "Cardiology")
            n_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        # Build metadata filter
        where_clause = {}
        if location_filter:
            where_clause["location"] = location_filter
        if specialty_filter:
            where_clause["primary_specialty"] = specialty_filter
        
        # Perform vector search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None,
            include=["metadatas", "distances", "documents"]
        )
        
        # Convert to SearchResult objects
        search_results = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            
            result = SearchResult(
                doctor_id=metadata['doctor_id'],
                name=metadata['name'],
                specialty=metadata['primary_specialty'],
                sub_specialty=metadata['sub_specialty'],
                location=metadata['location'],
                hospital=metadata['hospital_affiliation'],
                experience=metadata['years_of_experience'],
                languages=metadata['languages'],
                surgeries_summary=metadata['surgeries_summary'],
                expertise=metadata['expertise'],
                similarity_score=1 - distance  # Convert distance to similarity
            )
            search_results.append(result)
        
        return search_results
    
    def generate_recommendation(
        self, 
        patient_query: str, 
        search_results: List[SearchResult],
        include_reasoning: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an intelligent recommendation using LLM
        
        Args:
            patient_query: Original patient query
            search_results: List of doctors from vector search
            include_reasoning: Whether to include detailed reasoning
            
        Returns:
            Dictionary with recommendation and explanation
        """
        if not self.use_openai:
            return {
                "recommendation": search_results[0].to_dict() if search_results else None,
                "explanation": "LLM not configured. Returning top vector search result.",
                "alternative_options": [r.to_dict() for r in search_results[1:3]] if len(search_results) > 1 else []
            }
        
        # Prepare doctor profiles for the prompt
        doctor_profiles = "\n\n".join([
            f"Doctor {i+1}: {r.name}\n"
            f"- Specialty: {r.specialty} ({r.sub_specialty})\n"
            f"- Location: {r.location}\n"
            f"- Hospital: {r.hospital}\n"
            f"- Experience: {r.experience} years\n"
            f"- Languages: {r.languages}\n"
            f"- Expertise: {r.surgeries_summary}\n"
            f"- Special Interests: {r.expertise}"
            for i, r in enumerate(search_results)
        ])
        
        # Create the prompt
        system_prompt = """You are a medical assistant helping to match patients with the most suitable doctors. 
        Based on the patient's symptoms and the available doctor profiles, recommend the best doctor and explain why.
        Consider factors like specialty match, experience, location, and specific expertise.
        Always include a disclaimer that this is for informational purposes and patients should verify credentials."""
        
        user_prompt = f"""Patient Query: {patient_query}

Available Doctors (ranked by relevance):
{doctor_profiles}

Please provide:
1. Your top recommendation with detailed reasoning
2. Why this doctor is the best match for the patient's needs
3. Any alternative options if applicable
4. Important considerations or next steps for the patient"""
        
        try:
            # Make API call to OpenAI
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            llm_response = response.choices[0].message.content
            
            # Parse the recommendation
            # For simplicity, we'll assume the LLM recommends the first doctor most of the time
            # In production, you'd want more sophisticated parsing
            recommended_doctor = search_results[0] if search_results else None
            
            return {
                "recommendation": recommended_doctor.to_dict() if recommended_doctor else None,
                "explanation": llm_response,
                "alternative_options": [r.to_dict() for r in search_results[1:3]] if len(search_results) > 1 else [],
                "search_metadata": {
                    "total_results": len(search_results),
                    "query": patient_query,
                    "model_used": self.model_name
                }
            }
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return {
                "recommendation": search_results[0].to_dict() if search_results else None,
                "explanation": f"Error generating recommendation: {str(e)}. Returning top search result.",
                "alternative_options": [r.to_dict() for r in search_results[1:3]] if len(search_results) > 1 else []
            }
    
    def process_patient_query(
        self,
        query: str,
        location: Optional[str] = None,
        specialty: Optional[str] = None,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: Search + Generate recommendation
        
        Args:
            query: Patient's problem description
            location: Optional location filter
            specialty: Optional specialty filter
            n_results: Number of doctors to retrieve
            
        Returns:
            Complete recommendation with explanation
        """
        # Step 1: Vector search
        print(f"Searching for doctors matching: '{query}'")
        search_results = self.search_doctors(
            query=query,
            location_filter=location,
            specialty_filter=specialty,
            n_results=n_results
        )
        
        if not search_results:
            return {
                "success": False,
                "message": "No doctors found matching your criteria.",
                "recommendation": None
            }
        
        print(f"Found {len(search_results)} matching doctors")
        
        # Step 2: Generate recommendation
        print("Generating personalized recommendation...")
        recommendation = self.generate_recommendation(query, search_results)
        
        return {
            "success": True,
            "recommendation": recommendation,
            "timestamp": str(os.popen('date').read().strip())
        }

def main():
    """Example usage of the RAG system"""
    
    # Initialize RAG system
    # Note: Set OPENAI_API_KEY in your .env file to use LLM features
    # Without it, the system will still work but only return vector search results
    use_llm = os.getenv("OPENAI_API_KEY") is not None
    
    if not use_llm:
        print("\nNote: OPENAI_API_KEY not found in environment.")
        print("The system will work but without LLM-powered recommendations.")
        print("To enable LLM features, create a .env file with:")
        print("OPENAI_API_KEY=your-api-key-here\n")
    
    rag = SmartDoctorsRAG(use_openai=use_llm)
    
    # Example queries
    test_queries = [
        {
            "query": "I've been having severe chest pain and shortness of breath, especially when climbing stairs. I have a history of high blood pressure.",
            "location": "New York, NY"
        },
        {
            "query": "My 5-year-old daughter has recurring ear infections and hearing problems. We need someone who is good with children.",
            "location": "Boston, MA"
        },
        {
            "query": "I need a neurosurgeon for my back pain that radiates down my leg. I've tried physical therapy but it's getting worse.",
            "location": None  # No location filter
        }
    ]
    
    print("\n" + "="*50)
    print("SmartDoctors RAG System Demo")
    print("="*50)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n\nTest Case {i}:")
        print(f"Query: {test_case['query']}")
        if test_case.get('location'):
            print(f"Location Filter: {test_case['location']}")
        
        result = rag.process_patient_query(
            query=test_case['query'],
            location=test_case.get('location'),
            n_results=5
        )
        
        if result['success']:
            rec = result['recommendation']
            if rec['recommendation']:
                print(f"\nRecommended Doctor: {rec['recommendation']['name']}")
                print(f"Specialty: {rec['recommendation']['specialty']}")
                print(f"Location: {rec['recommendation']['location']}")
                
                print("\nExplanation:")
                print("-" * 30)
                print(rec['explanation'])
        else:
            print(f"Error: {result['message']}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    main()