# SmartDoctors - AI-Powered Doctor Recommendation System

A RAG (Retrieval-Augmented Generation) based system that helps match patients with the most suitable doctors based on their symptoms and medical needs.

![SmartDoctors Demo](https://img.shields.io/badge/AI-Powered-blue) ![Python](https://img.shields.io/badge/Python-3.11-green) ![FastAPI](https://img.shields.io/badge/FastAPI-Modern-red) ![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 🌟 Features

- **Semantic Search**: Find doctors based on symptom descriptions, not just keywords
- **AI-Powered Recommendations**: Uses LLM to provide intelligent doctor matches with explanations
- **Vector Database**: ChromaDB for efficient similarity search across 5000+ doctor profiles
- **RESTful API**: FastAPI backend with automatic documentation
- **Web Interface**: Clean, responsive UI for easy interaction
- **Location & Specialty Filtering**: Narrow down results by location and medical specialty
- **Works Without LLM**: Fallback to vector search if OpenAI API key not provided

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key (optional, but recommended for full features)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/smartdoctors.git
cd smartdoctors
```

### 2. Set up environment variables
Create a `.env` file:
```bash
# Optional: For AI-powered explanations
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Generate doctor data (first time only)
```bash
# Build the image
docker build -t smartdoctors .

# Generate synthetic doctor data
docker run -it --rm -v $(pwd):/app smartdoctors python generate_doctor_data.py
```

### 4. Run with Docker Compose
```bash
docker-compose up
```

The application will be available at `http://localhost:8000`

## 💻 Local Development Setup

### 1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate doctor data
```bash
python generate_doctor_data.py
```

### 4. Create embeddings
```bash
python create_embeddings.py
```

### 5. Run the API server
```bash
python api_server.py
```

Visit `http://localhost:8000` to use the application.

## 📋 API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /recommend` - Get doctor recommendations based on symptoms
- `POST /search` - Search doctors without AI explanations
- `GET /locations` - Get available locations
- `GET /specialties` - Get available specialties

### Example Request
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I have chest pain and shortness of breath",
    "location": "New York, NY",
    "n_results": 5
  }'
```

## 🏗️ Architecture

```
SmartDoctors/
├── api_server.py          # FastAPI backend
├── rag_system.py          # RAG implementation
├── create_embeddings.py   # Vector embedding generation
├── generate_doctor_data.py # Synthetic data generation
├── static/                # Frontend files
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── chroma_db/            # Vector database (generated)
└── doctors_data.json     # Doctor profiles (generated)
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `PORT`: API server port (default: 8000)

### Customization
- Modify `generate_doctor_data.py` to change doctor profiles
- Adjust embedding model in `create_embeddings.py`
- Update UI in `static/` directory

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 How It Works

1. **Data Generation**: Creates 5000 synthetic doctor profiles with specialties, locations, and expertise
2. **Embedding Creation**: Converts doctor profiles into semantic vectors using Sentence Transformers
3. **Vector Storage**: Stores embeddings in ChromaDB for fast similarity search
4. **Query Processing**: 
   - User enters symptoms
   - System converts query to vector
   - Finds most similar doctor vectors
   - Returns ranked results
5. **AI Enhancement** (if API key provided):
   - LLM analyzes matches
   - Provides detailed explanations
   - Suggests alternatives

## ⚠️ Disclaimer

This is a demonstration system for educational purposes. Always consult with real healthcare professionals for medical advice. The doctor profiles in this system are synthetic and not real medical practitioners.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Vector search powered by [ChromaDB](https://www.trychroma.com/)
- Embeddings from [Sentence Transformers](https://www.sbert.net/)
- UI inspired by modern healthcare applications

---

Made with ❤️ for better healthcare accessibility