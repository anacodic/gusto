// Format price range
export function formatPrice(priceRange) {
  if (typeof priceRange === 'number') {
    return '$'.repeat(Math.min(priceRange, 4));
  }
  return priceRange || 'N/A';
}

// Format distance
export function formatDistance(distance) {
  if (!distance) return 'N/A';
  if (distance < 1) {
    return `${Math.round(distance * 5280)} ft`;
  }
  return `${distance.toFixed(1)} mi`;
}

// Format rating
export function formatRating(rating) {
  if (!rating) return 'N/A';
  return `${rating.toFixed(1)}/5.0`;
}

// Format taste vector for display
export function formatTasteVector(vector) {
  if (!vector || vector.length !== 6) {
    return [0, 0, 0, 0, 0, 0];
  }
  return vector.map(v => Math.max(0, Math.min(1, v)));
}

// Format similarity score
export function formatSimilarity(score) {
  if (score === undefined || score === null) return 'N/A';
  return `${Math.round(score * 100)}%`;
}

// Format date
export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

// Format time ago
export function formatTimeAgo(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(dateString);
}
