#!/usr/bin/env python3
"""
Visualize doctor vectors in 2D using PCA and t-SNE
"""

import chromadb
from chromadb.config import Settings
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import seaborn as sns

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

# Initialize ChromaDB
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(anonymized_telemetry=False)
)

# Get the doctors collection
collection = client.get_collection(name="doctors")

print("Loading doctor vectors...")

# Get a larger sample of doctors with their embeddings
# We'll get 500 doctors for a good visualization
results = collection.get(
    limit=500,
    include=["embeddings", "metadatas"]
)

# Extract data
embeddings = np.array(results['embeddings'])
metadatas = results['metadatas']
specialties = [m['primary_specialty'] for m in metadatas]
names = [m['name'] for m in metadatas]

print(f"Loaded {len(embeddings)} doctor vectors")
print(f"Vector dimensions: {embeddings.shape}")

# Get unique specialties for coloring
unique_specialties = list(set(specialties))
color_map = {spec: i for i, spec in enumerate(unique_specialties)}
colors = [color_map[spec] for spec in specialties]

# Create figure with subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# 1. PCA Visualization (faster, linear)
print("\nApplying PCA...")
pca = PCA(n_components=2)
vectors_pca = pca.fit_transform(embeddings)

# Plot PCA
scatter1 = ax1.scatter(vectors_pca[:, 0], vectors_pca[:, 1], 
                      c=colors, cmap='tab10', alpha=0.6, s=50)
ax1.set_title('Doctor Vectors in 2D (PCA)', fontsize=16)
ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')

# Add specialty labels to PCA plot
for i, spec in enumerate(unique_specialties[:10]):  # Show first 10 specialties
    spec_mask = np.array(specialties) == spec
    center = vectors_pca[spec_mask].mean(axis=0)
    ax1.annotate(spec, center, fontsize=8, weight='bold')

# 2. t-SNE Visualization (slower, non-linear, better clustering)
print("Applying t-SNE (this may take a moment)...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
vectors_tsne = tsne.fit_transform(embeddings)

# Plot t-SNE
scatter2 = ax2.scatter(vectors_tsne[:, 0], vectors_tsne[:, 1], 
                      c=colors, cmap='tab10', alpha=0.6, s=50)
ax2.set_title('Doctor Vectors in 2D (t-SNE)', fontsize=16)
ax2.set_xlabel('t-SNE 1')
ax2.set_ylabel('t-SNE 2')

# Add specialty labels to t-SNE plot
for i, spec in enumerate(unique_specialties[:10]):  # Show first 10 specialties
    spec_mask = np.array(specialties) == spec
    center = vectors_tsne[spec_mask].mean(axis=0)
    ax2.annotate(spec, center, fontsize=8, weight='bold')

# Add legend
legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                            markerfacecolor=plt.cm.tab10(color_map[spec]), 
                            markersize=8, label=spec) 
                  for spec in unique_specialties[:10]]
ax2.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()
plt.savefig('doctor_vectors_2d.png', dpi=300, bbox_inches='tight')
print("\nSaved visualization to 'doctor_vectors_2d.png'")
plt.show()

# Create a second figure showing specialty clusters
fig2, ax3 = plt.subplots(1, 1, figsize=(12, 10))

# Use t-SNE results for detailed view
ax3.scatter(vectors_tsne[:, 0], vectors_tsne[:, 1], 
           c=colors, cmap='tab10', alpha=0.3, s=30)

# Highlight specific specialties with different markers
highlight_specs = ['Cardiology', 'Neurology', 'Pediatrics', 'Oncology']
markers = ['o', 's', '^', 'D']

for spec, marker in zip(highlight_specs, markers):
    if spec in specialties:
        spec_mask = np.array(specialties) == spec
        ax3.scatter(vectors_tsne[spec_mask, 0], vectors_tsne[spec_mask, 1], 
                   label=spec, marker=marker, s=100, alpha=0.8, edgecolors='black')

ax3.set_title('Doctor Specialties Clustering in Vector Space', fontsize=16)
ax3.set_xlabel('t-SNE Dimension 1')
ax3.set_ylabel('t-SNE Dimension 2')
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('doctor_specialties_clusters.png', dpi=300, bbox_inches='tight')
print("Saved specialty clusters to 'doctor_specialties_clusters.png'")
plt.show()

# Print some statistics
print("\nClustering Statistics:")
for spec in unique_specialties[:5]:
    spec_mask = np.array(specialties) == spec
    spec_vectors = embeddings[spec_mask]
    if len(spec_vectors) > 1:
        # Calculate average distance between doctors of same specialty
        distances = []
        for i in range(len(spec_vectors)):
            for j in range(i+1, len(spec_vectors)):
                dist = np.linalg.norm(spec_vectors[i] - spec_vectors[j])
                distances.append(dist)
        avg_distance = np.mean(distances) if distances else 0
        print(f"{spec}: {len(spec_vectors)} doctors, avg distance: {avg_distance:.3f}")

print("\nVisualization complete!")