import { useState, useEffect } from 'react';
import api from '../utils/api';

export function useGroups(userId = 'default') {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGroups = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.get(`/api/users/${userId}/groups`);
        setGroups(response.data.groups || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch groups');
        setGroups([]);
      } finally {
        setLoading(false);
      }
    };

    fetchGroups();
  }, [userId]);

  const createGroup = async (name, memberIds = []) => {
    try {
      const response = await api.post(`/api/users/${userId}/groups`, {
        name,
        member_ids: memberIds
      });
      setGroups([...groups, response.data]);
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to create group');
      throw err;
    }
  };

  const getGroupRecommendations = async (groupId) => {
    try {
      const response = await api.get(`/api/groups/${groupId}/recommendations`);
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to get recommendations');
      throw err;
    }
  };

  return { groups, loading, error, createGroup, getGroupRecommendations };
}
