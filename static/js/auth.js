// API endpoints
const API_URL = '/api/auth';

// Login function
async function login(username, password) {
    try {
        const response = await fetch('/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        });

        const data = await response.json();
        
        if (response.ok) {
            return data;
        } else {
            throw new Error(data.message || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

// Register function
async function register(userData) {
    try {
        const response = await fetch('/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(userData),
            credentials: 'include'
        });

        const data = await response.json();
        
        if (response.ok) {
            return data;
        } else {
            throw new Error(data.message || 'Registration failed');
        }
    } catch (error) {
        console.error('Registration error:', error);
        throw error;
    }
}

// Logout function
document.getElementById('logoutLink').addEventListener('click', async function(event) {
    event.preventDefault();  // Ngừng hành động mặc định của thẻ <a> (không điều hướng)

    // Xóa token JWT khỏi localStorage hoặc cookies
    localStorage.removeItem('jwtToken');  // Hoặc xóa token từ cookies nếu bạn lưu ở đó

    try {
        const response = await fetch('/api/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),  // CSRF token nếu bạn dùng Django
            },
            credentials: 'include',  // Đảm bảo rằng cookie sẽ được gửi cùng yêu cầu
        });

        if (!response.ok) {
            throw new Error('Logout failed');
        }

        const data = await response.json();
        if (data.message === "Logout successful.") {
            // Nếu logout thành công, chuyển hướng về trang chủ
            window.location.href = '/home';
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
});

// Check if user is authenticated
async function isAuthenticated() {
    try {
        const response = await fetch(`${API_URL}/status/`, {
            credentials: 'include'
        });
        return response.ok;
    } catch (error) {
        console.error('Auth check error:', error);
        return false;
    }
}

// Get current user
async function getCurrentUser() {
    try {
        const response = await fetch(`${API_URL}/status/`, {
            credentials: 'include'
        });
        if (response.ok) {
            return await response.json();
        }
        return null;
    } catch (error) {
        console.error('Get user error:', error);
        return null;
    }
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Export functions
export {
    login,
    register,
    logout,
    isAuthenticated,
    getCurrentUser
}; 