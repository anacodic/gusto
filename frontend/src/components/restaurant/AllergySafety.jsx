import './AllergySafety.css';

function AllergySafety({ dishes, allergies }) {
  if (!allergies || allergies.length === 0) {
    return null;
  }

  const safeDishes = dishes?.filter(dish => {
    if (!dish.allergy_info) return true;
    return !allergies.some(allergy => 
      dish.allergy_info.toLowerCase().includes(allergy.toLowerCase())
    );
  }) || [];

  const unsafeDishes = dishes?.filter(dish => {
    if (!dish.allergy_info) return false;
    return allergies.some(allergy => 
      dish.allergy_info.toLowerCase().includes(allergy.toLowerCase())
    );
  }) || [];

  return (
    <div className="allergy-safety">
      <h4>🛡️ Allergy Safety</h4>
      <div className="allergy-warning">
        <strong>Your allergies: {allergies.join(', ')}</strong>
      </div>
      
      {safeDishes.length > 0 && (
        <div className="safe-dishes">
          <strong>✅ Safe dishes ({safeDishes.length}):</strong>
          <ul>
            {safeDishes.slice(0, 5).map((dish, i) => (
              <li key={i}>{dish.name || dish}</li>
            ))}
          </ul>
        </div>
      )}
      
      {unsafeDishes.length > 0 && (
        <div className="unsafe-dishes">
          <strong>⚠️ Avoid these dishes ({unsafeDishes.length}):</strong>
          <ul>
            {unsafeDishes.slice(0, 5).map((dish, i) => (
              <li key={i}>{dish.name || dish}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default AllergySafety;
