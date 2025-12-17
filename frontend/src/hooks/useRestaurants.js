import { useState, useEffect } from 'react';
import api from '../utils/api';

export function useRestaurants(query = '', location = '', filters = {}) {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!query && !location) {
      setRestaurants([]);
      return;
    }

    const fetchRestaurants = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.post('/api/chat', {
          query: query || `restaurants in ${location}`,
          location: location,
          max_results: filters.maxResults || 10,
          ...filters
        });
        
        if (response.data.menu_buddy?.recommendations) {
          setRestaurants(response.data.menu_buddy.recommendations);
        } else {
          setRestaurants([]);
        }
      } catch (err) {
        setError(err.message || 'Failed to fetch restaurants');
        setRestaurants([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRestaurants();
  }, [query, location, JSON.stringify(filters)]);

  return { restaurants, loading, error, refetch: () => {
    // Trigger refetch by updating a dependency
    setRestaurants([...restaurants]);
  }};
}
