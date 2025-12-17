import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import TasteProfile from '../components/restaurant/TasteProfile';
import BeerPairing from '../components/restaurant/BeerPairing';
import AllergySafety from '../components/restaurant/AllergySafety';
import RecommendedDishes from '../components/restaurant/RecommendedDishes';
import './RestaurantDetails.css';

function RestaurantDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [restaurant, setRestaurant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Try to get restaurant from API or local storage
    const fetchRestaurant = async () => {
      try {
        // Check if restaurant data is in location state (from navigation)
        const state = window.history.state?.usr;
        if (state?.restaurant) {
          setRestaurant(state.restaurant);
          setLoading(false);
          return;
        }
        
        // Try API call
        try {
          const response = await api.get(`/api/restaurants/${id}`);
          setRestaurant(response.data);
        } catch (apiError) {
          console.error('Error fetching restaurant:', apiError);
          // If restaurant not found, show error
          if (apiError.response?.status === 404) {
            setError('Restaurant not found');
          } else {
            setError('Failed to load restaurant details');
          }
        }
      } catch (err) {
        setError('Failed to load restaurant details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRestaurant();
  }, [id]);

  if (loading) {
    return (
      <div className="restaurant-details-page">
        <div className="loading">Loading restaurant details...</div>
      </div>
    );
  }

  if (error || !restaurant) {
    return (
      <div className="restaurant-details-page">
        <div className="error">
          <p>{error || 'Restaurant not found'}</p>
          <Link to="/">← Back to Discover</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="restaurant-details-page">
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="back-link">← Back</button>
        <button className="save-btn">❤️ Save</button>
      </div>
      
      <div className="restaurant-hero">
        <h1>{restaurant.name}</h1>
        <div className="restaurant-meta">
          {restaurant.avg_rating && (
            <span>⭐ {restaurant.avg_rating.toFixed(1)} ({restaurant.review_count || 0} reviews)</span>
          )}
          {restaurant.price_range && (
            <span>{'$'.repeat(restaurant.price_range)}</span>
          )}
          {restaurant.cuisine_types && (
            <span>{restaurant.cuisine_types.join(', ')}</span>
          )}
          {restaurant.location && (
            <span>📍 {typeof restaurant.location === 'string' ? restaurant.location : restaurant.location.address || restaurant.location.city || 'Location not available'}</span>
          )}
        </div>
      </div>

      <div className="restaurant-content">
        <div className="main-content">
          <TasteProfile 
            tasteVector={restaurant.taste_vector} 
            label="Restaurant Taste Profile"
          />
          
          {restaurant.recommended_dishes && restaurant.recommended_dishes.length > 0 && (
            <RecommendedDishes dishes={restaurant.recommended_dishes} />
          )}
          
          <BeerPairing restaurant={restaurant} />
        </div>

        <div className="sidebar">
          <AllergySafety 
            dishes={restaurant.recommended_dishes || []}
            allergies={restaurant.user_allergies || []}
          />
          
          {restaurant.photos && restaurant.photos.length > 0 && (
            <div className="restaurant-photos">
              <h4>Photos</h4>
              <div className="photos-grid">
                {restaurant.photos.slice(0, 4).map((photo, i) => (
                  <img key={i} src={photo} alt={`${restaurant.name} photo ${i + 1}`} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default RestaurantDetails;
