import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import RestaurantCard from '../components/restaurant/RestaurantCard';
import './Discover.css';

function Discover() {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRestaurants();
  }, []);

  const loadRestaurants = async () => {
    try {
      // Use the discover endpoint
      const response = await api.get('/api/restaurants/discover', {
        params: {
          location: 'Boston, MA',
          max_results: 20
        }
      });
      
      if (response.data?.restaurants) {
        setRestaurants(response.data.restaurants);
      }
    } catch (error) {
      console.error('Error loading restaurants:', error);
      // Fallback to empty array on error
      setRestaurants([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="discover-page">Loading...</div>;
  }

  return (
    <div className="discover-page">
      <div className="discover-header">
        <h1>🔍 Discover Feed</h1>
      </div>
      
      <div className="restaurants-grid">
        {restaurants.map((restaurant, index) => (
          <RestaurantCard 
            key={restaurant.id || index} 
            restaurant={restaurant}
          />
        ))}
      </div>
      
      {restaurants.length === 0 && (
        <div className="empty-state">
          <p>No restaurants found. Try searching in chat!</p>
          <Link to="/chat">Go to Chat</Link>
        </div>
      )}
    </div>
  );
}

export default Discover;
