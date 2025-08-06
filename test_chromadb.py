#!/usr/bin/env python3
"""
Test script to verify ChromaDB initialization
"""

import chromadb
from chromadb.config import Settings
import os
import shutil

CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "doctors"

def test_chromadb():
    """Test ChromaDB initialization with schema handling"""
    
    print(f"Testing ChromaDB at {CHROMA_PERSIST_DIR}")
    
    # Option 1: Try to connect to existing database
    try:
        client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Try to get the collection
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"✓ Successfully connected to existing collection: {COLLECTION_NAME}")
        print(f"  Collection has {collection.count()} items")
        
    except Exception as e:
        print(f"✗ Error with existing database: {e}")
        
        # Option 2: Clear and recreate
        response = input("\nWould you like to clear the database and start fresh? (y/n): ")
        if response.lower() == 'y':
            # Remove the old database
            if os.path.exists(CHROMA_PERSIST_DIR):
                shutil.rmtree(CHROMA_PERSIST_DIR)
                print(f"  Removed old database at {CHROMA_PERSIST_DIR}")
            
            # Create new database
            client = chromadb.PersistentClient(
                path=CHROMA_PERSIST_DIR,
                settings=Settings(anonymized_telemetry=False)
            )
            
            collection = client.create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "Doctor profiles for SmartDoctors RAG system"}
            )
            print(f"✓ Created new collection: {COLLECTION_NAME}")
            print("  Run 'python create_embeddings.py' to populate with data")
        else:
            print("Database not modified. You may need to manually fix the schema issue.")

if __name__ == "__main__":
    test_chromadb()