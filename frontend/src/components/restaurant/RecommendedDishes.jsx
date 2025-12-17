import './RecommendedDishes.css';

function RecommendedDishes({ dishes, userTasteVector }) {
  if (!dishes || dishes.length === 0) {
    return null;
  }

  return (
    <div className="recommended-dishes">
      <h4>🍽️ Recommended Dishes</h4>
      <div className="dishes-list">
        {dishes.map((dish, i) => (
          <div key={i} className="dish-item">
            <div className="dish-header">
              <strong>{dish.name || dish}</strong>
              {dish.similarity !== undefined && (
                <span className="similarity-score">
                  {Math.round(dish.similarity * 100)}% match
                </span>
              )}
            </div>
            {dish.description && (
              <p className="dish-description">{dish.description}</p>
            )}
            {dish.taste_vector && (
              <div className="dish-taste-preview">
                {['Sweet', 'Salty', 'Sour', 'Bitter', 'Umami', 'Spicy'].map((label, idx) => (
                  <span key={label} className="taste-tag">
                    {label}: {dish.taste_vector[idx]?.toFixed(1) || 0}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default RecommendedDishes;
