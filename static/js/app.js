// Marketing Platform JavaScript

// Global variables
let currentUser = null;

// Utility Functions
function showAlert(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        <i class="bi bi-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    // Auto remove
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'primary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function formatDate(dateString) {
    if (!dateString) return 'No date set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function getTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return `${Math.ceil(diffDays / 30)} months ago`;
}

function setLoadingState(element, isLoading, originalText = '') {
    if (isLoading) {
        element.disabled = true;
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = '<i class="bi bi-arrow-clockwise spin me-1"></i>Loading...';
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || originalText;
    }
}

// Authentication Functions
async function logout() {
    try {
        await fetch('/auth/logout', { method: 'POST' });
        showAlert('Logged out successfully', 'success');
        setTimeout(() => {
            window.location.href = '/auth/login';
        }, 1000);
    } catch (error) {
        window.location.href = '/auth/login';
    }
}

async function checkAuthStatus() {
    try {
        const response = await fetch('/auth/status');
        const data = await response.json();
        return data.authenticated ? data.user : null;
    } catch (error) {
        return null;
    }
}

// Project Functions
async function fetchProjects() {
    try {
        const response = await fetch('/api/projects/');
        if (!response.ok) {
            throw new Error('Failed to fetch projects');
        }
        return await response.json();
    } catch (error) {
        showAlert('Error loading projects: ' + error.message, 'danger');
        return { projects: [], count: 0 };
    }
}

async function createProject(projectData) {
    try {
        const response = await fetch('/api/projects/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`Project "${data.project.name}" created successfully!`, 'success');
            return data;
        } else {
            throw new Error(data.error || 'Failed to create project');
        }
    } catch (error) {
        showAlert('Error creating project: ' + error.message, 'danger');
        throw error;
    }
}

async function deleteProject(projectId, projectName) {
    if (!confirm(`Are you sure you want to delete "${projectName}"? This action cannot be undone.`)) {
        return false;
    }
    
    try {
        const response = await fetch(`/api/projects/${projectId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Project deleted successfully!', 'success');
            return true;
        } else {
            throw new Error(data.error || 'Failed to delete project');
        }
    } catch (error) {
        showAlert('Error deleting project: ' + error.message, 'danger');
        return false;
    }
}

async function fetchProjectDetails(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch project details');
        }
        return await response.json();
    } catch (error) {
        showAlert('Error loading project details: ' + error.message, 'danger');
        return null;
    }
}

// UI Helper Functions
function getStatusBadgeClass(status) {
    const statusClasses = {
        'active': 'bg-success',
        'completed': 'bg-primary',
        'paused': 'bg-warning',
        'cancelled': 'bg-danger'
    };
    return statusClasses[status] || 'bg-secondary';
}

function getProgressBarClass(progress) {
    if (progress >= 80) return 'bg-success';
    if (progress >= 50) return 'bg-warning';
    return 'bg-danger';
}

function createProjectCard(project) {
    return `
        <div class="project-card fade-in" data-project-id="${project.id}">
            <div class="project-header">
                <h6 class="project-title">${project.name}</h6>
                <span class="badge ${getStatusBadgeClass(project.status)}">${project.status.toUpperCase()}</span>
            </div>
            
            <p class="project-description">${project.description || 'No description provided'}</p>
            
            <div class="project-meta">
                <small class="text-muted">
                    <i class="bi bi-person me-1"></i>${project.owner}
                </small>
                <small class="text-muted">
                    <i class="bi bi-calendar me-1"></i>${formatDate(project.due_date)}
                </small>
            </div>
            
            <div class="progress-container">
                <div class="progress-label">
                    <span>Progress</span>
                    <span class="fw-bold">${project.progress}%</span>
                </div>
                <div class="progress">
                    <div class="progress-bar ${getProgressBarClass(project.progress)}" 
                         style="width: ${project.progress}%"></div>
                </div>
            </div>
            
            <div class="d-flex justify-content-between align-items-center mt-3">
                <small class="text-muted">
                    <i class="bi bi-list-task me-1"></i>${project.task_count} tasks
                </small>
                <div class="project-actions">
                    <button class="btn btn-outline-primary btn-sm" onclick="viewProjectDetails(${project.id})">
                        <i class="bi bi-eye me-1"></i>View
                    </button>
                    ${currentUser && currentUser.role === 'admin' ? `
                    <button class="btn btn-outline-danger btn-sm" onclick="handleDeleteProject(${project.id}, '${project.name}')">
                        <i class="bi bi-trash me-1"></i>Delete
                    </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

// Event Handlers
async function handleDeleteProject(projectId, projectName) {
    const success = await deleteProject(projectId, projectName);
    if (success && typeof loadProjects === 'function') {
        loadProjects();
    }
}

function viewProjectDetails(projectId) {
    setTimeout(() => {
        window.location.href = `/project/${projectId}`;
    }, 500);
}

// Navigation Functions
function showProjects() {
    showAlert('Projects view coming soon!', 'info');
}

function showAnalytics() {
    showAlert('Analytics view coming soon!', 'info');
}

function showAutomation() {
    showAlert('Automation view coming soon!', 'info');
}

function showUsers() {
    showAlert('User management view coming soon!', 'info');
}

// Form Validation
function validateProjectForm(formData) {
    const errors = [];
    
    if (!formData.name || formData.name.trim().length < 3) {
        errors.push('Project name must be at least 3 characters long');
    }
    
    if (formData.due_date) {
        const dueDate = new Date(formData.due_date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (dueDate < today) {
            errors.push('Due date cannot be in the past');
        }
    }
    
    return errors;
}

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated on protected pages
    const isAuthPage = window.location.pathname.includes('/auth/');
    
    if (!isAuthPage) {
        checkAuthStatus().then(user => {
            if (!user) {
                window.location.href = '/auth/login';
            } else {
                currentUser = user;
                // Initialize page-specific functionality
                if (typeof initializePage === 'function') {
                    initializePage();
                }
            }
        });
    }
});

// CSS Animation Classes
const animationStyles = `
.fade-in {
    animation: fadeIn 0.5s ease-in;
}

.slide-up {
    animation: slideUp 0.3s ease-out;
}

.spin {
    animation: spin 1s linear infinite;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
    from { transform: translateY(30px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = animationStyles;
document.head.appendChild(styleSheet);