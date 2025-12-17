import { useState, useEffect } from 'react';
import api from '../utils/api';

export function useCollections(userId = 'default') {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCollections = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.get(`/api/users/${userId}/collections`);
        setCollections(response.data.collections || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch collections');
        setCollections([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCollections();
  }, [userId]);

  const createCollection = async (name, description = '') => {
    try {
      const response = await api.post(`/api/users/${userId}/collections`, {
        name,
        description
      });
      setCollections([...collections, response.data]);
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to create collection');
      throw err;
    }
  };

  const addToCollection = async (collectionId, restaurantId) => {
    try {
      await api.post(`/api/collections/${collectionId}/restaurants`, {
        restaurant_id: restaurantId
      });
      // Refresh collections
      const response = await api.get(`/api/users/${userId}/collections`);
      setCollections(response.data.collections || []);
    } catch (err) {
      setError(err.message || 'Failed to add restaurant');
      throw err;
    }
  };

  return { collections, loading, error, createCollection, addToCollection };
}
