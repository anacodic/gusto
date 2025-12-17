import './BeerPairing.css';

function BeerPairing({ restaurant, dish }) {
  const beerPairing = restaurant?.beer_pairing || dish?.beer_pairing;
  
  if (!beerPairing) {
    return null;
  }

  return (
    <div className="beer-pairing">
      <h4>🍺 Beer Pairing</h4>
      {beerPairing.recommendations && beerPairing.recommendations.length > 0 ? (
        <div className="beer-recommendations">
          {beerPairing.recommendations.map((beer, i) => (
            <div key={i} className="beer-item">
              <strong>{beer.name}</strong>
              {beer.description && <p>{beer.description}</p>}
              {beer.rating && <span>⭐ {beer.rating.toFixed(1)}/5.0</span>}
              {beer.confidence && (
                <span className="confidence">Match: {Math.round(beer.confidence * 100)}%</span>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p>No beer pairing available for this dish.</p>
      )}
    </div>
  );
}

export default BeerPairing;
