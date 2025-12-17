import './TasteProfile.css';

function TasteProfile({ tasteVector, label = "Taste Profile" }) {
  const tasteLabels = ['Sweet', 'Salty', 'Sour', 'Bitter', 'Umami', 'Spicy'];
  const vector = tasteVector || [0, 0, 0, 0, 0, 0];

  return (
    <div className="taste-profile">
      <h4>{label}</h4>
      <div className="taste-bars-container">
        {tasteLabels.map((label, i) => (
          <div key={label} className="taste-bar-row">
            <span className="taste-label">{label}</span>
            <div className="taste-bar">
              <div 
                className="taste-fill" 
                style={{ width: `${Math.min(vector[i] * 100, 100)}%` }}
              />
            </div>
            <span className="taste-value">{(vector[i] || 0).toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TasteProfile;
