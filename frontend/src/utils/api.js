import axios from 'axios';
import { userPool } from '../auth/cognitoConfig';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to all requests
api.interceptors.request.use(async (config) => {
  try {
    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      const session = await new Promise((resolve, reject) => {
        cognitoUser.getSession((err, session) => {
          if (err) reject(err);
          else resolve(session);
        });
      });
      if (session && session.isValid()) {
        config.headers.Authorization = `Bearer ${session.getIdToken().getJwtToken()}`;
      }
    }
  } catch (error) {
    console.error('Error getting token:', error);
  }
  return config;
});

export default api;
