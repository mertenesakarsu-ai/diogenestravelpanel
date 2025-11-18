import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL
});

// Add request interceptor to include user ID in headers
api.interceptors.request.use(
  (config) => {
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        if (user && user.id) {
          config.headers['x-user-id'] = user.id;
        }
      } catch (error) {
        console.error('Error parsing user from localStorage:', error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('currentUser');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      // Forbidden - show error message
      console.error('Permission denied:', error.response.data?.detail);
    }
    return Promise.reject(error);
  }
);

export default api;
