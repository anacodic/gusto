import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import './Collections.css';

function Collections() {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      const response = await api.get('/api/collections');
      setCollections(response.data.collections || []);
    } catch (error) {
      console.error('Error loading collections:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="collections-page">
      <div className="collections-header">
        <h1>📌 My Collections</h1>
        <button className="new-collection-btn">+ New Collection</button>
      </div>
      
      <div className="collections-grid">
        {collections.map((collection) => (
          <Link 
            key={collection.id} 
            to={`/collections/${collection.id}`}
            className="collection-card"
          >
            <div className="collection-emoji">{collection.emoji}</div>
            <div className="collection-name">{collection.name}</div>
            <div className="collection-count">{collection.restaurant_count} places</div>
          </Link>
        ))}
      </div>
      
      {collections.length === 0 && (
        <div className="empty-state">
          <p>No collections yet. Create one to save your favorite restaurants!</p>
        </div>
      )}
    </div>
  );
}

export default Collections;
