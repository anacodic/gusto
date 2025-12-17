import React, { useState } from 'react';
import RestaurantModal from './RestaurantModal';
import './StoryCard.css';

function StoryCard({ restaurant, index }) {
  const [showModal, setShowModal] = useState(false);

  const handleViewDetails = () => {
    setShowModal(true);
  };

  // Generate story intro text based on index
  const storyIntros = [
    "🌸 Once upon a time in Boston...",
    "🌸 And then there was...",
    "🌸 In a cozy corner...",
    "🌸 Hidden away...",
    "🌸 A delightful discovery..."
  ];

  const storyIntro = storyIntros[index % storyIntros.length];

  // Format price range
  const priceDisplay = restaurant.price_range 
    ? '$'.repeat(Math.min(restaurant.price_range, 4))
    : '$$';

  // Format rating
  const rating = restaurant.rating || restaurant.avg_rating;
  const ratingDisplay = rating ? (typeof rating === 'number' ? `${rating}/5` : rating) : 'N/A';

  // Get recommended dishes
  const dishes = restaurant.recommended_dishes || [];

  return (
    <div className="story-card">
      <div className="story-intro">{storyIntro}</div>
      
      <div className="restaurant-photo">
        {restaurant.photos && restaurant.photos.length > 0 ? (
          <img 
            src={restaurant.photos[0]} 
            alt={restaurant.name}
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/400x300/f0f0f0/999?text=Restaurant+Photo';
            }}
          />
        ) : (
          <div className="placeholder-photo">
            <span>📸</span>
          </div>
        )}
      </div>

      <div className="restaurant-info">
        <h3 className="restaurant-name">{restaurant.name}</h3>
        <div className="restaurant-meta">
          <span className="rating">⭐ {ratingDisplay}</span>
          {restaurant.review_count && (
            <>
              <span className="separator">|</span>
              <span className="reviews">({restaurant.review_count} reviews)</span>
            </>
          )}
          <span className="separator">|</span>
          <span className="location">
            📍 {restaurant.location?.city || restaurant.location?.formatted_address?.split(',')[0] || 'Location'}
          </span>
          <span className="separator">|</span>
          <span className="price">{priceDisplay}</span>
        </div>

        <p className="restaurant-description">
          {restaurant.description || restaurant.summary || restaurant.contextual_info?.summary || `A hidden gem where flavors come alive...`}
        </p>

        {dishes.length > 0 && (
          <div className="recommended-dishes">
            <div className="dishes-label">🍽️ Perfect for you:</div>
            <div className="dishes-list">
              {dishes.slice(0, 3).map((dish, idx) => (
                <div key={idx} className="dish-item">
                  <span className="dish-name">
                    • {dish.name || dish}
                  </span>
                  {dish.similarity && (
                    <span className="dish-match">
                      ({dish.similarity}% match)
                      {dish.similarity > 80 && ' 🌶️'}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="card-actions">
          <button 
            className="details-btn"
            onClick={handleViewDetails}
          >
            View Details
          </button>
        </div>
      </div>

      <RestaurantModal 
        restaurant={restaurant}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
      />
    </div>
  );
}

export default StoryCard;
