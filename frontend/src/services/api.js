/**
 * API service for backend communication.
 * 
 * Handles all HTTP requests to the CloudOps backend API.
 * Includes error handling and request/response formatting.
 */

import axios from 'axios';

// Create axios instance with default config
const API = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Request interceptor
API.interceptors.request.use(
    (config) => {
        // Add auth token if available
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
API.interceptors.response.use(
    (response) => response.data,
    (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

// ============ HEALTH CHECK ============
export const healthCheck = () => API.get('/health/ready');

// ============ DEPLOYMENTS ============
export const deployments = {
    list: (params) => API.get('/deployments', { params }),
    get: (id) => API.get(`/deployments/${id}`),
    create: (data) => API.post('/deployments', data),
    update: (id, data) => API.patch(`/deployments/${id}`, data),
    rollback: (id) => API.post(`/deployments/${id}/rollback`),
    history: (id, limit = 10) => 
        API.get(`/deployments/${id}/history`, { params: { limit } })
};

// ============ INCIDENTS ============
export const incidents = {
    list: (params) => API.get('/incidents', { params }),
    get: (id) => API.get(`/incidents/${id}`),
    create: (data) => API.post('/incidents', data),
    update: (id, data) => API.patch(`/incidents/${id}`, data),
    stats: (id) => API.get(`/incidents/${id}/stats`)
};

// ============ METRICS ============
export const metrics = {
    list: (params) => API.get('/metrics', { params })
};

export default API;
