#!/usr/bin/env python3
"""
View the actual vectors stored in ChromaDB
"""

import chromadb
from chromadb.config import Settings
import numpy as np

# Initialize ChromaDB
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(anonymized_telemetry=False)
)

# Get the doctors collection
collection = client.get_collection(name="doctors")

print("="*60)
print("ChromaDB Vector Viewer")
print("="*60)

# Get total count
total_docs = collection.count()
print(f"\nTotal doctors in database: {total_docs}")

# Get a sample of doctors with their embeddings
print("\nFetching sample doctors with their vectors...")
results = collection.get(
    limit=5,  # Get first 5 doctors
    include=["embeddings", "metadatas", "documents"]
)

print(f"\nShowing {len(results['ids'])} doctors:\n")

for i in range(len(results['ids'])):
    doctor_id = results['ids'][i]
    metadata = results['metadatas'][i]
    embedding = results['embeddings'][i]
    
    print(f"Doctor {i+1}:")
    print(f"  ID: {doctor_id}")
    print(f"  Name: {metadata['name']}")
    print(f"  Specialty: {metadata['primary_specialty']}")
    print(f"  Location: {metadata['location']}")
    
    # Show vector statistics
    embedding_array = np.array(embedding)
    print(f"\n  Vector Information:")
    print(f"    - Dimensions: {len(embedding)}")
    print(f"    - Min value: {embedding_array.min():.4f}")
    print(f"    - Max value: {embedding_array.max():.4f}")
    print(f"    - Mean value: {embedding_array.mean():.4f}")
    print(f"    - First 10 values: {embedding[:10]}")
    print(f"    - Last 10 values: {embedding[-10:]}")
    print("-"*60)

# Let's also show how similar vectors are
print("\n\nVector Similarity Example:")
print("Let's compare two doctors' vectors...")

if len(results['ids']) >= 2:
    # Get first two doctors' embeddings
    vec1 = np.array(results['embeddings'][0])
    vec2 = np.array(results['embeddings'][1])
    
    # Calculate cosine similarity
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    cosine_similarity = dot_product / (norm1 * norm2)
    
    print(f"\nDoctor 1: {results['metadatas'][0]['name']} ({results['metadatas'][0]['primary_specialty']})")
    print(f"Doctor 2: {results['metadatas'][1]['name']} ({results['metadatas'][1]['primary_specialty']})")
    print(f"Cosine Similarity: {cosine_similarity:.4f}")
    print(f"(1.0 = identical, 0 = unrelated, -1 = opposite)")

# Show a query example
print("\n\nQuery Example:")
print("Let's search for 'heart problems' and see the vectors...")

query_results = collection.query(
    query_texts=["heart problems"],
    n_results=3,
    include=["embeddings", "metadatas", "distances"]
)

if query_results['ids'][0]:
    print("\nTop 3 matches for 'heart problems':")
    for i in range(len(query_results['ids'][0])):
        metadata = query_results['metadatas'][0][i]
        distance = query_results['distances'][0][i]
        similarity = 1 - distance
        
        print(f"\n{i+1}. {metadata['name']}")
        print(f"   Specialty: {metadata['primary_specialty']}")
        print(f"   Similarity Score: {similarity:.4f}")
        print(f"   Distance: {distance:.4f}")

print("\n" + "="*60)