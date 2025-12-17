import { CognitoUserPool } from 'amazon-cognito-identity-js';

// Use Vite environment variables (import.meta.env.VITE_*)
const poolData = {
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID || import.meta.env.REACT_APP_COGNITO_USER_POOL_ID || 'us-east-1_jUJj5G3YE',
  ClientId: import.meta.env.VITE_COGNITO_CLIENT_ID || import.meta.env.REACT_APP_COGNITO_CLIENT_ID || '7krp0ucjkl3gehlm2iolcdukka',
};

let userPool;
try {
  userPool = new CognitoUserPool(poolData);
} catch (error) {
  throw error;
}

export { userPool };

export const getCognitoUser = (username) => {
  return userPool.getCurrentUser();
};
