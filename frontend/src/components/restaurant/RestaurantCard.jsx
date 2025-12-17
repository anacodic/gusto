import { Link } from 'react-router-dom';
import './RestaurantCard.css';

function RestaurantCard({ restaurant, showGroupScores = false, groupMembers = [] }) {
  const tasteVector = restaurant.taste_vector || [0, 0, 0, 0, 0, 0];
  const tasteLabels = ['Sweet', 'Salty', 'Sour', 'Bitter', 'Umami', 'Spicy'];
  const tasteMatch = restaurant.score ? Math.round(restaurant.score * 100) : 0;

  return (
    <div className="restaurant-card">
      <div className="restaurant-photo">
        {restaurant.photos?.[0] ? (
          <img src={restaurant.photos[0]} alt={restaurant.name} />
        ) : (
          <div className="photo-placeholder">📸</div>
        )}
      </div>
      
      <div className="restaurant-info">
        <h3>{restaurant.name}</h3>
        <div className="restaurant-meta">
          {restaurant.avg_rating && (
            <span>⭐ {restaurant.avg_rating} ({restaurant.review_count || 0} reviews)</span>
          )}
          {restaurant.price_range && (
            <span>{'$'.repeat(restaurant.price_range)}</span>
          )}
          {restaurant.cuisine_types && (
            <span>{restaurant.cuisine_types.join(', ')}</span>
          )}
        </div>

        <div className="taste-match">
          <strong>📊 Taste Match: {tasteMatch}%</strong>
          <div className="taste-bars">
            {tasteLabels.map((label, i) => (
              <div key={label} className="taste-bar-row">
                <span className="taste-label">{label}</span>
                <div className="taste-bar">
                  <div 
                    className="taste-fill" 
                    style={{ width: `${tasteVector[i] * 100}%` }}
                  />
                </div>
                <span className="taste-value">{tasteVector[i]?.toFixed(1) || 0}</span>
              </div>
            ))}
          </div>
        </div>

        {restaurant.recommended_dishes && restaurant.recommended_dishes.length > 0 && (
          <div className="recommended-dishes">
            <strong>🍽️ Recommended Dishes:</strong>
            <ul>
              {restaurant.recommended_dishes.slice(0, 3).map((dish, i) => (
                <li key={i}>
                  {dish.name || dish} ({Math.round((dish.similarity || 0) * 100)}% match)
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="restaurant-actions">
          <button>❤️ Save</button>
          <button>📤 Share</button>
          <Link to={`/restaurants/${restaurant.id}`}>
            <button>View Details</button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default RestaurantCard;
