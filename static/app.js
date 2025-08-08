// SmartDoctors Frontend Application

const API_BASE_URL = ''; // Works in all environments (local, Docker, Railway)

// DOM Elements
const searchForm = document.getElementById('searchForm');
const symptomsInput = document.getElementById('symptoms');
const locationSelect = document.getElementById('location');
const specialtySelect = document.getElementById('specialty');
const searchBtn = document.getElementById('searchBtn');
const loadingDiv = document.getElementById('loading');
const resultsSection = document.getElementById('results');
const errorDiv = document.getElementById('error');
const newSearchBtn = document.getElementById('newSearchBtn');
const exampleButtons = document.querySelectorAll('.example-btn');

// Event Listeners
searchForm.addEventListener('submit', handleSearch);
newSearchBtn.addEventListener('click', resetSearch);

// Handle example buttons
exampleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        symptomsInput.value = btn.dataset.query;
        // Auto-focus on symptoms field
        symptomsInput.focus();
    });
});

// Handle search submission
async function handleSearch(e) {
    e.preventDefault();
    
    // Get form values
    const symptoms = symptomsInput.value.trim();
    const location = locationSelect.value;
    const specialty = specialtySelect.value;
    
    if (!symptoms) {
        alert('Please describe your symptoms or medical concerns');
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: symptoms,
                location: location || null,
                specialty: specialty || null,
                n_results: 5
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get recommendations');
        }
        
        const data = await response.json();
        
        if (data.success && data.recommendation) {
            displayResults(data.recommendation);
        } else {
            showError('No doctors found matching your criteria. Please try different search terms.');
        }
        
    } catch (error) {
        console.error('Search error:', error);
        showError('Unable to get recommendations. Please check your connection and try again.');
    }
}

// Display search results
function displayResults(recommendation) {
    hideAllStates();
    resultsSection.classList.remove('hidden');
    
    // Display primary recommendation
    if (recommendation.recommendation) {
        displayPrimaryRecommendation(recommendation.recommendation);
    }
    
    // Display AI explanation
    if (recommendation.explanation) {
        displayExplanation(recommendation.explanation);
    }
    
    // Display alternative options
    if (recommendation.alternative_options && recommendation.alternative_options.length > 0) {
        displayAlternatives(recommendation.alternative_options);
    }
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display primary doctor recommendation
function displayPrimaryRecommendation(doctor) {
    const container = document.getElementById('primaryRecommendation');
    
    container.innerHTML = `
        <div class="doctor-card">
            <div class="doctor-header">
                <span class="doctor-badge">✓ Top Match</span>
                <span class="match-score">${(doctor.similarity_score * 100).toFixed(0)}% Match</span>
            </div>
            
            <h3 class="doctor-name">${doctor.name}</h3>
            <p class="doctor-specialty">${doctor.specialty} - ${doctor.sub_specialty}</p>
            
            <div class="doctor-details">
                <div class="detail-item">
                    <span class="detail-label">Location</span>
                    <span class="detail-value">${doctor.location}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Hospital</span>
                    <span class="detail-value">${doctor.hospital}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Experience</span>
                    <span class="detail-value">${doctor.experience} years</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Languages</span>
                    <span class="detail-value">${doctor.languages}</span>
                </div>
            </div>
            
            <div class="doctor-summary">
                <h4>Clinical Experience</h4>
                <p>${doctor.surgeries_summary}</p>
            </div>
            
            <div class="doctor-summary">
                <h4>Special Interests & Expertise</h4>
                <p>${doctor.expertise}</p>
            </div>
        </div>
    `;
}

// Display AI explanation
function displayExplanation(explanation) {
    const container = document.getElementById('aiExplanation');
    
    container.innerHTML = `
        <h3>AI Analysis & Recommendation</h3>
        <div class="explanation-content">${explanation}</div>
    `;
}

// Display alternative doctors
function displayAlternatives(alternatives) {
    const container = document.getElementById('alternativeOptions');
    
    if (alternatives.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<h3>Alternative Options</h3>';
    
    alternatives.forEach((doctor, index) => {
        html += `
            <div class="alternative-card">
                <h4>${doctor.name}</h4>
                <p class="doctor-specialty">${doctor.specialty} - ${doctor.sub_specialty}</p>
                <div class="doctor-details">
                    <div class="detail-item">
                        <span class="detail-label">Location</span>
                        <span class="detail-value">${doctor.location}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Hospital</span>
                        <span class="detail-value">${doctor.hospital}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Experience</span>
                        <span class="detail-value">${doctor.experience} years</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Match Score</span>
                        <span class="detail-value">${(doctor.similarity_score * 100).toFixed(0)}%</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Show loading state
function showLoading() {
    hideAllStates();
    loadingDiv.classList.remove('hidden');
    searchBtn.disabled = true;
}

// Show error state
function showError(message) {
    hideAllStates();
    errorDiv.innerHTML = `<p>${message}</p>`;
    errorDiv.classList.remove('hidden');
}

// Hide all states
function hideAllStates() {
    loadingDiv.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorDiv.classList.add('hidden');
    searchBtn.disabled = false;
}

// Reset search
function resetSearch() {
    searchForm.reset();
    hideAllStates();
    window.scrollTo({ top: 0, behavior: 'smooth' });
    symptomsInput.focus();
}

// Check API health on load
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('API Status:', data);
        
        if (!data.llm_enabled) {
            console.warn('LLM features are disabled. Only vector search will be used.');
        }
    } catch (error) {
        console.error('API health check failed:', error);
        showError('Unable to connect to the server. Please make sure the API is running.');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAPIHealth();
    symptomsInput.focus();
});