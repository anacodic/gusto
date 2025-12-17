import { useState, useEffect } from 'react';
import { useAuth } from '../auth/AuthContext';
import api from '../utils/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar } from 'recharts';
import './Profile.css';

function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadProfile();
    loadStats();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await api.get('/api/users/profile');
      setProfile(response.data);
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const loadStats = async () => {
    try {
      // Load collections count and calculate saved restaurants
      const collectionsRes = await api.get('/api/collections');
      const collections = collectionsRes.data.collections || [];
      const collectionsCount = collections.length;
      
      // Calculate total saved restaurants across all collections
      let savedCount = 0;
      for (const collection of collections) {
        try {
          const collectionRes = await api.get(`/api/collections/${collection.id}`);
          savedCount += collectionRes.data.restaurants?.length || 0;
        } catch (err) {
          // If collection fetch fails, use restaurant_count if available
          savedCount += collection.restaurant_count || 0;
        }
      }
      
      // Load friends count
      const friendsRes = await api.get('/api/friends');
      const friendsCount = friendsRes.data.friends?.length || 0;
      
      // Load groups count
      const groupsRes = await api.get('/api/groups');
      const groupsCount = groupsRes.data.groups?.length || 0;
      
      setStats({
        collections: collectionsCount,
        friends: friendsCount,
        groups: groupsCount,
        saved: savedCount
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  if (!profile) {
    return <div>Loading...</div>;
  }

  const tasteData = [
    { name: 'Sweet', value: profile.taste_vector?.[0] || 0 },
    { name: 'Salty', value: profile.taste_vector?.[1] || 0 },
    { name: 'Sour', value: profile.taste_vector?.[2] || 0 },
    { name: 'Bitter', value: profile.taste_vector?.[3] || 0 },
    { name: 'Umami', value: profile.taste_vector?.[4] || 0 },
    { name: 'Spicy', value: profile.taste_vector?.[5] || 0 },
  ];

  return (
    <div className="profile-page">
      <div className="profile-header">
        <h1>👤 Your Taste Profile</h1>
        <button className="settings-btn">Settings</button>
      </div>

      <div className="profile-section">
        <h2>📊 Current Taste Profile</h2>
        <div className="taste-bars">
          {tasteData.map((item) => (
            <div key={item.name} className="taste-bar-item">
              <div className="taste-label">{item.name}</div>
              <div className="taste-bar">
                <div 
                  className="taste-fill" 
                  style={{ width: `${item.value * 100}%` }}
                />
              </div>
              <div className="taste-value">{item.value.toFixed(1)}</div>
            </div>
          ))}
        </div>
      </div>

      {stats && (
        <div className="profile-section">
          <h2>📌 Statistics</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{stats.saved}</div>
              <div className="stat-label">Saved restaurants</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.collections}</div>
              <div className="stat-label">Collections</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.friends}</div>
              <div className="stat-label">Friends</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.groups}</div>
              <div className="stat-label">Groups</div>
            </div>
          </div>
        </div>
      )}

      <div className="profile-section">
        <h2>Profile Info</h2>
        <div className="profile-info">
          <p><strong>Name:</strong> {profile.name}</p>
          <p><strong>Email:</strong> {profile.email}</p>
          <p><strong>Location:</strong> {profile.location || 'Not set'}</p>
          <p><strong>Diet Type:</strong> {profile.diet_type}</p>
          <p><strong>Allergies:</strong> {profile.allergies?.join(', ') || 'None'}</p>
        </div>
      </div>
    </div>
  );
}

export default Profile;
