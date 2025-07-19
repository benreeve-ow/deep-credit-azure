/**
 * Deep Credit Azure - Frontend JavaScript
 * 
 * This file handles:
 * - Form submission and validation
 * - API communication with Flask backend
 * - Results display and formatting
 * - User interface interactions
 */

// Wait for the DOM to be fully loaded before running our code
document.addEventListener('DOMContentLoaded', function() {
    console.log('Deep Credit Azure frontend loaded');
    
    // Initialize the application
    initializeApp();
});

/**
 * Initialize the application and set up event listeners
 */
function initializeApp() {
    // Get references to important DOM elements
    const form = document.getElementById('creditAnalysisForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorSection = document.getElementById('errorSection');
    const resultsSection = document.getElementById('resultsSection');
    
    // Set up form submission handler
    if (form) {
        form.addEventListener('submit', handleFormSubmission);
    }
    
    // Add some interactive enhancements
    addFormValidation();
    addUIEnhancements();
    
    console.log('Application initialized successfully');
}

/**
 * Handle form submission for credit analysis
 * @param {Event} event - The form submission event
 */
async function handleFormSubmission(event) {
    // Prevent the default form submission behavior
    event.preventDefault();
    
    // Get form data
    const creditData = document.getElementById('creditData').value.trim();
    const analysisType = document.getElementById('analysisType').value;
    
    // Validate input
    if (!creditData) {
        showError('Please enter your credit information');
        return;
    }
    
    // Show loading state
    showLoadingState();
    
    try {
        // Send request to backend API
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                credit_data: creditData,
                analysis_type: analysisType
            })
        });
        
        // Parse the response
        const result = await response.json();
        
        if (response.ok) {
            // Success - display results
            displayResults(result);
        } else {
            // Error response from server
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze credit profile. Please try again.');
    } finally {
        // Hide loading state
        hideLoadingState();
    }
}

/**
 * Display the analysis results in the results section
 * @param {Object} results - The analysis results from the API
 */
function displayResults(results) {
    const resultsContainer = document.getElementById('analysisResults');
    const resultsSection = document.getElementById('resultsSection');
    
    // Clear any previous results
    resultsContainer.innerHTML = '';
    
    // Create results HTML
    let resultsHTML = '';
    
    // Check if we have a proper analysis result
    if (results.analysis) {
        resultsHTML = `
            <div class="alert alert-info">
                <h5>Analysis Complete!</h5>
                <p><strong>Analysis Type:</strong> ${results.analysis_type || 'Basic'}</p>
                <p><strong>Result:</strong> ${results.analysis}</p>
                <p><strong>Data Processed:</strong> ${results.credit_data_received ? 'Yes' : 'No'}</p>
            </div>
        `;
    } else if (results.credit_score_assessment) {
        // Full structured analysis result
        resultsHTML = createStructuredResultsHTML(results);
    } else {
        // Fallback for any other response format
        resultsHTML = `
            <div class="alert alert-warning">
                <h5>Analysis Completed</h5>
                <pre>${JSON.stringify(results, null, 2)}</pre>
            </div>
        `;
    }
    
    // Insert the results HTML
    resultsContainer.innerHTML = resultsHTML;
    
    // Show the results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Create structured HTML for detailed analysis results
 * @param {Object} results - The structured analysis results
 * @returns {string} - HTML string for the results
 */
function createStructuredResultsHTML(results) {
    return `
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">
                        <h5>📊 Credit Score Assessment</h5>
                    </div>
                    <div class="card-body">
                        <p>${results.credit_score_assessment}</p>
                        ${results.overall_rating ? `<p><strong>Overall Rating:</strong> ${results.overall_rating}/10</p>` : ''}
                    </div>
                </div>
                
                <div class="card mb-3">
                    <div class="card-header">
                        <h5>💡 Recommendations</h5>
                    </div>
                    <div class="card-body">
                        ${results.recommendations ? createListHTML(results.recommendations) : '<p>No recommendations available</p>'}
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">
                        <h5>⚠️ Risk Factors</h5>
                    </div>
                    <div class="card-body">
                        ${results.risk_factors ? createListHTML(results.risk_factors) : '<p>No risk factors identified</p>'}
                    </div>
                </div>
                
                <div class="card mb-3">
                    <div class="card-header">
                        <h5>📋 Financial Health Summary</h5>
                    </div>
                    <div class="card-body">
                        <p>${results.financial_health_summary || 'Summary not available'}</p>
                    </div>
                </div>
            </div>
        </div>
        
        ${results.analysis_timestamp ? `
            <div class="text-muted text-center mt-3">
                <small>Analysis completed at ${new Date(results.analysis_timestamp * 1000).toLocaleString()}</small>
            </div>
        ` : ''}
    `;
}

/**
 * Create an HTML list from an array of items
 * @param {Array} items - Array of items to display
 * @returns {string} - HTML string for the list
 */
function createListHTML(items) {
    if (!Array.isArray(items) || items.length === 0) {
        return '<p>No items available</p>';
    }
    
    const listItems = items.map(item => `<li>${item}</li>`).join('');
    return `<ul>${listItems}</ul>`;
}

/**
 * Show loading state while analysis is in progress
 */
function showLoadingState() {
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('errorSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Disable the submit button
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '⏳ Analyzing...';
    }
}

/**
 * Hide loading state when analysis is complete
 */
function hideLoadingState() {
    document.getElementById('loadingSpinner').style.display = 'none';
    
    // Re-enable the submit button
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = false;
        submitButton.innerHTML = '🔍 Analyze Credit Profile';
    }
}

/**
 * Display an error message to the user
 * @param {string} message - The error message to display
 */
function showError(message) {
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Scroll to error message
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Add form validation enhancements
 */
function addFormValidation() {
    const creditDataField = document.getElementById('creditData');
    
    if (creditDataField) {
        // Add character counter
        const charCounter = document.createElement('div');
        charCounter.className = 'form-text text-end';
        charCounter.id = 'charCounter';
        creditDataField.parentNode.appendChild(charCounter);
        
        // Update character count
        function updateCharCount() {
            const length = creditDataField.value.length;
            charCounter.textContent = `${length} characters`;
            
            // Change color based on length
            if (length < 50) {
                charCounter.className = 'form-text text-end text-warning';
            } else if (length > 1000) {
                charCounter.className = 'form-text text-end text-danger';
            } else {
                charCounter.className = 'form-text text-end text-success';
            }
        }
        
        creditDataField.addEventListener('input', updateCharCount);
        updateCharCount(); // Initial call
    }
}

/**
 * Add UI enhancements for better user experience
 */
function addUIEnhancements() {
    // Add hover effects to form elements
    const formControls = document.querySelectorAll('.form-control, .form-select');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.3)';
        });
        
        control.addEventListener('blur', function() {
            this.style.boxShadow = '';
        });
    });
    
    // Add smooth transitions
    const style = document.createElement('style');
    style.textContent = `
        .form-control, .form-select, .btn {
            transition: all 0.3s ease;
        }
        
        .results-section, .error-section {
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// Utility function to check system health
async function checkSystemHealth() {
    try {
        const response = await fetch('/api/health');
        const health = await response.json();
        console.log('System health:', health);
        return health.status === 'healthy';
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

// Export functions for testing or external use
window.DeepCreditAzure = {
    checkSystemHealth,
    displayResults,
    showError,
    showLoadingState,
    hideLoadingState
}; 