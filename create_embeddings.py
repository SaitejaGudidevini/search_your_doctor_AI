#!/usr/bin/env python3
"""
Embedding Generation for SmartDoctors
Creates vector embeddings for doctor profiles and stores them in ChromaDB
"""

import json
import os
import shutil
from typing import List, Dict, Any
from tqdm import tqdm
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime

# Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fast and efficient
# Alternative models:
# "sentence-transformers/all-mpnet-base-v2"  # Better quality, slower
# "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"  # Medical-specific

CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "doctors"
BATCH_SIZE = 100

class DoctorEmbeddingPipeline:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize the embedding pipeline"""
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection with proper error handling
        try:
            # Try to get existing collection first
            self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)
            print(f"Using existing collection: {COLLECTION_NAME}")
            print(f"  Collection has {self.collection.count()} items")
        except Exception as e:
            # If collection doesn't exist or has schema issues, handle it
            print(f"Collection issue detected: {str(e)[:100]}")
            
            # Check if it's a schema issue
            if "no such column" in str(e):
                print("Schema mismatch detected. Recreating database...")
                # Remove the entire database directory for a clean start
                try:
                    if os.path.exists(CHROMA_PERSIST_DIR):
                        shutil.rmtree(CHROMA_PERSIST_DIR)
                        print(f"Removed old database at {CHROMA_PERSIST_DIR}")
                except Exception as rm_err:
                    print(f"Warning: Could not remove old database: {rm_err}")
                    # Try to at least remove the SQLite file
                    try:
                        db_file = os.path.join(CHROMA_PERSIST_DIR, "chroma.sqlite3")
                        if os.path.exists(db_file):
                            os.remove(db_file)
                            print(f"Removed SQLite file: {db_file}")
                    except:
                        pass
                
                # Recreate client with fresh database
                os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(
                    path=CHROMA_PERSIST_DIR,
                    settings=Settings(anonymized_telemetry=False)
                )
            
            # Create new collection
            self.collection = self.chroma_client.create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "Doctor profiles for SmartDoctors RAG system"}
            )
            print(f"Created new collection: {COLLECTION_NAME}")
    
    def create_embedding_text(self, doctor: Dict[str, Any]) -> str:
        """
        Create a rich text representation of the doctor for embedding.
        This combines all relevant fields into a searchable text.
        """
        # Build comprehensive text that captures all aspects of the doctor's profile
        text_parts = [
            f"{doctor['primary_specialty']} specialist",
            f"subspecialty in {doctor['sub_specialty']}",
            f"practicing at {doctor['hospital_affiliation']}",
            f"located in {doctor['location']}",
            f"with {doctor['years_of_experience']} years of experience",
            f"Languages: {', '.join(doctor['language_fluency'])}",
            doctor['critical_surgeries_summary'],
            doctor['special_interests_and_expertise']
        ]
        
        return " ".join(text_parts)
    
    def prepare_metadata(self, doctor: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare metadata for storage in ChromaDB.
        ChromaDB requires metadata values to be strings, ints, floats, or bools.
        """
        return {
            "doctor_id": doctor["doctor_id"],
            "name": doctor["name"],
            "primary_specialty": doctor["primary_specialty"],
            "sub_specialty": doctor["sub_specialty"],
            "location": doctor["location"],
            "hospital_affiliation": doctor["hospital_affiliation"],
            "years_of_experience": doctor["years_of_experience"],
            "languages": ", ".join(doctor["language_fluency"]),  # Convert list to string
            "language_count": len(doctor["language_fluency"]),
            # Store the full text fields for retrieval
            "surgeries_summary": doctor["critical_surgeries_summary"],
            "expertise": doctor["special_interests_and_expertise"]
        }
    
    def generate_embeddings(self, doctors: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings for a batch of doctors"""
        texts = [self.create_embedding_text(doc) for doc in doctors]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def process_doctors(self, doctors_file: str):
        """Process all doctors from JSON file and store in ChromaDB"""
        # Load doctors data
        print(f"Loading doctors from {doctors_file}")
        with open(doctors_file, 'r') as f:
            doctors = json.load(f)
        
        print(f"Found {len(doctors)} doctors to process")
        
        # Process in batches
        total_processed = 0
        
        for i in tqdm(range(0, len(doctors), BATCH_SIZE), desc="Processing batches"):
            batch = doctors[i:i + BATCH_SIZE]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(batch)
            
            # Prepare data for ChromaDB
            ids = [doc["doctor_id"] for doc in batch]
            documents = [self.create_embedding_text(doc) for doc in batch]
            metadatas = [self.prepare_metadata(doc) for doc in batch]
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            total_processed += len(batch)
        
        print(f"\nSuccessfully processed {total_processed} doctors")
        print(f"Database saved to: {CHROMA_PERSIST_DIR}")
    
    def test_search(self, query: str, n_results: int = 5):
        """Test the search functionality"""
        print(f"\nTesting search with query: '{query}'")
        
        # Generate embedding for query
        query_embedding = self.model.encode([query]).tolist()
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["metadatas", "distances", "documents"]
        )
        
        print(f"\nTop {n_results} results:")
        for i, (metadata, distance, document) in enumerate(zip(
            results['metadatas'][0], 
            results['distances'][0],
            results['documents'][0]
        )):
            print(f"\n{i+1}. {metadata['name']}")
            print(f"   Specialty: {metadata['primary_specialty']} - {metadata['sub_specialty']}")
            print(f"   Location: {metadata['location']}")
            print(f"   Hospital: {metadata['hospital_affiliation']}")
            print(f"   Experience: {metadata['years_of_experience']} years")
            print(f"   Languages: {metadata['languages']}")
            print(f"   Similarity Score: {1 - distance:.4f}")  # Convert distance to similarity

def main():
    """Main function to run the embedding pipeline"""
    
    # Initialize pipeline
    pipeline = DoctorEmbeddingPipeline()
    
    # Process doctors data
    doctors_file = "indian_doctors_dataset.json"
    if not os.path.exists(doctors_file):
        print(f"Error: {doctors_file} not found. Please run generate_doctor_data.py first.")
        return
    
    # Generate and store embeddings
    pipeline.process_doctors(doctors_file)
    
    # Test search functionality
    print("\n" + "="*50)
    print("Testing search functionality")
    print("="*50)
    
    test_queries = [
        "I want to see a doctor in New Delhi",
        "pediatric specialist who speaks Spanish",
        "neurologist experienced in epilepsy treatment",
        "cancer specialist in Boston",
        "orthopedic surgeon for sports injuries"
    ]
    
    for query in test_queries:
        pipeline.test_search(query, n_results=3)
        print("-" * 50)

if __name__ == "__main__":
    main()