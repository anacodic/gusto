import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import RestaurantCard from '../components/restaurant/RestaurantCard';
import './CollectionDetails.css';

function CollectionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [collection, setCollection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCollection();
  }, [id]);

  const loadCollection = async () => {
    try {
      const response = await api.get(`/api/collections/${id}`);
      setCollection(response.data);
    } catch (err) {
      console.error('Error loading collection:', err);
      setError('Failed to load collection');
    } finally {
      setLoading(false);
    }
  };

  const removeRestaurant = async (restaurantId) => {
    try {
      await api.delete(`/api/collections/${id}/restaurants/${restaurantId}`);
      // Reload collection after removal
      loadCollection();
    } catch (err) {
      console.error('Error removing restaurant:', err);
      alert('Failed to remove restaurant from collection');
    }
  };

  if (loading) {
    return (
      <div className="collection-details-page">
        <div className="loading">Loading collection...</div>
      </div>
    );
  }

  if (error || !collection) {
    return (
      <div className="collection-details-page">
        <div className="error">
          <p>{error || 'Collection not found'}</p>
          <Link to="/collections">← Back to Collections</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="collection-details-page">
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="back-link">← Back</button>
        <div className="header-actions">
          <button className="edit-btn">Edit</button>
          <button className="share-btn">Share</button>
        </div>
      </div>

      <div className="collection-hero">
        <div className="collection-emoji-large">{collection.emoji}</div>
        <h1>{collection.name}</h1>
        <p className="collection-count">{collection.restaurants?.length || 0} places</p>
      </div>

      <div className="restaurants-grid">
        {collection.restaurants && collection.restaurants.length > 0 ? (
          collection.restaurants.map((restaurant, index) => (
            <div key={restaurant.id || index} className="restaurant-item">
              <RestaurantCard 
                restaurant={{
                  id: restaurant.restaurant_id,
                  name: restaurant.restaurant_name,
                  ...restaurant.restaurant_data
                }}
              />
              <button 
                className="remove-btn"
                onClick={() => removeRestaurant(restaurant.restaurant_id)}
                title="Remove from collection"
              >
                ✕
              </button>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <p>No restaurants in this collection yet.</p>
            <Link to="/">Discover Restaurants</Link>
          </div>
        )}
      </div>
    </div>
  );
}

export default CollectionDetails;
