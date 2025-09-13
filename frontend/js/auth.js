// Authentication utility functions

/**
 * Check if user is authenticated
 * @returns {boolean} True if user is authenticated
 */
function isAuthenticated() {
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    return !!(token && userData);
}

/**
 * Get current user data
 * @returns {Object|null} User object or null if not authenticated
 */
function getCurrentUser() {
    const userData = localStorage.getItem('userData');
    if (userData) {
        try {
            return JSON.parse(userData);
        } catch (e) {
            console.error('Error parsing user data:', e);
            return null;
        }
    }
    return null;
}

/**
 * Check if current user has specific role
 * @param {string} role - Role to check for
 * @returns {boolean} True if user has the role
 */
function hasRole(role) {
    const user = getCurrentUser();
    return user && user.role === role;
}

/**
 * Check if current user is admin
 * @returns {boolean} True if user is admin
 */
function isAdmin() {
    return hasRole('admin');
}

/**
 * Redirect to login if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        alert('Access denied. Please login first.');
        window.location.href = '/login';
        return false;
    }
    return true;
}

/**
 * Redirect to home if not admin
 */
function requireAdmin() {
    if (!requireAuth()) return false;
    
    if (!isAdmin()) {
        alert('Access denied. Admin privileges required.');
        window.location.href = '/';
        return false;
    }
    return true;
}

/**
 * Make authenticated API request
 * @param {string} url - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise<Response|null>} Response or null if authentication failed
 */
async function makeAuthenticatedRequest(url, options = {}) {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        alert('Authentication required. Please login.');
        window.location.href = '/login';
        return null;
    }
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {})
        }
    };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (response.status === 401 || response.status === 403) {
            alert('Session expired or access denied. Please login again.');
            logout();
            return null;
        }
        
        return response;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Logout user and redirect to login
 */
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    window.location.href = '/login';
}

/**
 * Redirect based on user role after login
 * @param {Object} user - User object
 */
function redirectAfterLogin(user) {
    if (user.role === 'admin') {
        window.location.href = '/admin';
    } else {
        window.location.href = '/';
    }
}

/**
 * Update navigation UI based on authentication status
 */
function updateNavigationUI() {
    const user = getCurrentUser();
    
    // You can customize this based on your navigation structure
    if (user) {
        // User is logged in
        console.log(`Logged in as: ${user.firstName} ${user.lastName} (${user.role})`);
        
        // Show/hide navigation elements based on role
        const adminElements = document.querySelectorAll('.admin-only');
        adminElements.forEach(element => {
            element.style.display = user.role === 'admin' ? 'block' : 'none';
        });
        
        const userElements = document.querySelectorAll('.user-only');
        userElements.forEach(element => {
            element.style.display = user.role === 'user' ? 'block' : 'none';
        });
    } else {
        // User is not logged in
        const authRequiredElements = document.querySelectorAll('.auth-required');
        authRequiredElements.forEach(element => {
            element.style.display = 'none';
        });
    }
}

// Initialize authentication check when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateNavigationUI();
});
