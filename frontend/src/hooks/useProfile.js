import { useState, useEffect } from 'react';
import api from '../utils/api';

export function useProfile(userId = 'default') {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tasteHistory, setTasteHistory] = useState([]);

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.get(`/api/users/${userId}`);
        setProfile(response.data);
        
        // Fetch taste history if available
        if (response.data.taste_history) {
          setTasteHistory(response.data.taste_history);
        }
      } catch (err) {
        setError(err.message || 'Failed to fetch profile');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [userId]);

  const updateProfile = async (updates) => {
    try {
      const response = await api.put(`/api/users/${userId}`, updates);
      setProfile(response.data);
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to update profile');
      throw err;
    }
  };

  const updateTastePreferences = async (tasteVector) => {
    try {
      const response = await api.put(`/api/users/${userId}/taste`, {
        taste_vector: tasteVector
      });
      setProfile(prev => ({ ...prev, taste_vector: tasteVector }));
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to update taste preferences');
      throw err;
    }
  };

  return {
    profile,
    tasteHistory,
    loading,
    error,
    updateProfile,
    updateTastePreferences
  };
}
