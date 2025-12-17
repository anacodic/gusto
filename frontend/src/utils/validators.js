// Validate email
export function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Validate password
export function validatePassword(password) {
  if (!password) return { valid: false, error: 'Password is required' };
  if (password.length < 8) {
    return { valid: false, error: 'Password must be at least 8 characters' };
  }
  return { valid: true };
}

// Validate location
export function validateLocation(location) {
  if (!location || location.trim().length === 0) {
    return { valid: false, error: 'Location is required' };
  }
  if (location.length < 2) {
    return { valid: false, error: 'Location must be at least 2 characters' };
  }
  return { valid: true };
}

// Validate taste vector
export function validateTasteVector(vector) {
  if (!Array.isArray(vector) || vector.length !== 6) {
    return { valid: false, error: 'Taste vector must have 6 dimensions' };
  }
  for (let i = 0; i < vector.length; i++) {
    const value = vector[i];
    if (typeof value !== 'number' || value < 0 || value > 1) {
      return { valid: false, error: `Taste value at index ${i} must be between 0 and 1` };
    }
  }
  return { valid: true };
}

// Validate query
export function validateQuery(query) {
  if (!query || query.trim().length === 0) {
    return { valid: false, error: 'Query cannot be empty' };
  }
  if (query.length > 500) {
    return { valid: false, error: 'Query must be less than 500 characters' };
  }
  return { valid: true };
}

// Validate collection name
export function validateCollectionName(name) {
  if (!name || name.trim().length === 0) {
    return { valid: false, error: 'Collection name is required' };
  }
  if (name.length > 50) {
    return { valid: false, error: 'Collection name must be less than 50 characters' };
  }
  return { valid: true };
}

// Validate group name
export function validateGroupName(name) {
  if (!name || name.trim().length === 0) {
    return { valid: false, error: 'Group name is required' };
  }
  if (name.length > 50) {
    return { valid: false, error: 'Group name must be less than 50 characters' };
  }
  return { valid: true };
}
