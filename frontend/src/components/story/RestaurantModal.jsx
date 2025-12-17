import React from 'react';
import './RestaurantModal.css';

function RestaurantModal({ restaurant, isOpen, onClose }) {
  if (!isOpen || !restaurant) return null;

  const priceDisplay = restaurant.price_range 
    ? '$'.repeat(Math.min(restaurant.price_range, 4))
    : '$$';

  const rating = restaurant.rating || restaurant.avg_rating;
  const ratingDisplay = rating ? (typeof rating === 'number' ? `${rating}/5` : rating) : 'N/A';

  const dishes = restaurant.recommended_dishes || [];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <div className="modal-header">
          {restaurant.photos && restaurant.photos.length > 0 && (
            <img 
              src={restaurant.photos[0]} 
              alt={restaurant.name}
              className="modal-photo"
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/600x400/f0f0f0/999?text=Restaurant+Photo';
              }}
            />
          )}
          <h2 className="modal-title">{restaurant.name}</h2>
          <div className="modal-meta">
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
          
          {restaurant.location?.formatted_address && (
            <div className="modal-address">
              📍 {restaurant.location.formatted_address}
            </div>
          )}
          
          {restaurant.phone && (
            <div className="modal-phone">
              📞 {restaurant.phone}
            </div>
          )}
        </div>

        <div className="modal-body">
          <div className="modal-section">
            <h3>About</h3>
            <p className="modal-description">
              {restaurant.description || restaurant.summary || restaurant.contextual_info?.summary || `A delightful restaurant offering amazing flavors and great dining experience.`}
            </p>
          </div>
          
          {restaurant.photos && restaurant.photos.length > 1 && (
            <div className="modal-section">
              <h3>Photos</h3>
              <div className="modal-photos-grid">
                {restaurant.photos.slice(1, 5).map((photo, idx) => (
                  <img 
                    key={idx}
                    src={photo} 
                    alt={`${restaurant.name} photo ${idx + 2}`}
                    className="modal-photo-thumb"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {restaurant.cuisine_types && restaurant.cuisine_types.length > 0 && (
            <div className="modal-section">
              <h3>Cuisine</h3>
              <div className="cuisine-tags">
                {restaurant.cuisine_types.map((cuisine, idx) => (
                  <span key={idx} className="cuisine-tag">{cuisine}</span>
                ))}
              </div>
            </div>
          )}

          {dishes.length > 0 && (
            <div className="modal-section">
              <h3>🍽️ Recommended Dishes</h3>
              <div className="modal-dishes">
                {dishes.map((dish, idx) => (
                  <div key={idx} className="modal-dish-item">
                    <span className="dish-name">{dish.name || dish}</span>
                    {dish.similarity && (
                      <span className="dish-match">
                        {dish.similarity}% match
                        {dish.similarity > 80 && ' 🌶️'}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="modal-section modal-actions">
            {restaurant.url && (
              <a 
                href={restaurant.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="yelp-link"
              >
                View on Yelp →
              </a>
            )}
            {restaurant.menu_url && (
              <a 
                href={restaurant.menu_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="menu-link"
              >
                View Menu →
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default RestaurantModal;
