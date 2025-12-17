// Taste dimension labels
export const TASTE_LABELS = ['Sweet', 'Salty', 'Sour', 'Bitter', 'Umami', 'Spicy'];

// Price symbols
export const PRICE_SYMBOLS = {
  1: '$',
  2: '$$',
  3: '$$$',
  4: '$$$$'
};

// Cuisine types
export const CUISINE_TYPES = [
  'American', 'Italian', 'Chinese', 'Japanese', 'Thai', 'Indian',
  'Mexican', 'French', 'Mediterranean', 'Korean', 'Vietnamese', 'Greek'
];

// Agent types
export const AGENT_TYPES = {
  ORCHESTRATOR: 'orchestrator',
  YELP: 'yelp_agent',
  FLAVOR: 'flavor_agent',
  BEVERAGE: 'beverage_agent',
  BUDGET: 'budget_agent'
};

// Agent labels
export const AGENT_LABELS = {
  orchestrator: '🎯 Orchestrator',
  yelp_agent: '🔍 Yelp Discovery',
  flavor_agent: '👅 Taste Analysis',
  beverage_agent: '🍺 Beer Pairing',
  budget_agent: '💰 Budget Filter'
};

// API endpoints
export const API_ENDPOINTS = {
  CHAT: '/api/chat',
  RESTAURANTS: '/api/restaurants',
  USERS: '/api/users',
  COLLECTIONS: '/api/collections',
  GROUPS: '/api/groups',
  FRIENDS: '/api/friends'
};

// Default values
export const DEFAULTS = {
  MAX_RESULTS: 10,
  TASTE_VECTOR_SIZE: 6,
  PAGE_SIZE: 20
};
