import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  AuthenticationDetails,
  CognitoUser,
  CognitoUserAttribute,
} from 'amazon-cognito-identity-js';
import { userPool } from './cognitoConfig';
import api from '../utils/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    console.log('AuthProvider: Starting auth check...');
    console.log('AuthProvider: Initial loading state:', loading);
    // Set a maximum timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      if (loading) {
        console.warn('AuthProvider: Auth check timeout - setting loading to false');
        setLoading(false);
      }
    }, 3000); // 3 second max timeout
    
    checkAuthState().finally(() => {
      clearTimeout(timeoutId);
    });
  }, []);

  const checkAuthState = async () => {
    try {
      // Add timeout to prevent hanging
      const timeoutPromise = new Promise((resolve) => {
        setTimeout(() => {
          console.warn('Auth check timeout - proceeding without auth');
          resolve(null);
        }, 2000); // 2 second timeout
      });

      const authCheckPromise = new Promise((resolve) => {
        try {
          const cognitoUser = userPool.getCurrentUser();
          
          if (cognitoUser) {
            cognitoUser.getSession((err, session) => {
              if (err || !session || !session.isValid()) {
                resolve(null);
                return;
              }
              cognitoUser.getUserAttributes((err, attributes) => {
                if (err) {
                  resolve(null);
                  return;
                }
                const userData = {};
                attributes.forEach((attr) => {
                  userData[attr.Name] = attr.Value;
                });
                const userInfo = {
                  username: cognitoUser.getUsername(),
                  email: userData.email,
                  name: userData.name || userData.email,
                  ...userData,
                };
                resolve({ userInfo, token: session.getIdToken().getJwtToken() });
              });
            });
          } else {
            resolve(null);
          }
        } catch (error) {
          console.error('Error in auth check:', error);
          resolve(null);
        }
      });

      const result = await Promise.race([authCheckPromise, timeoutPromise]);
      
      if (result && result.userInfo) {
        setUser(result.userInfo);
        setIsAuthenticated(true);
        syncUserWithBackend(result.token);
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
      
      setLoading(false);
      console.log('AuthProvider: setLoading(false) called, isAuthenticated:', isAuthenticated);
    } catch (error) {
      console.error('Error checking auth state:', error);
      setUser(null);
      setIsAuthenticated(false);
      setLoading(false);
    }
  };

  const syncUserWithBackend = async (token) => {
    try {
      const response = await api.post('/api/users/sync', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data) {
        setUser(prev => ({ ...prev, ...response.data }));
        localStorage.setItem('user_id', response.data.id);
      }
    } catch (error) {
      console.error('Error syncing user:', error);
    }
  };

  const signIn = (email, password) => {
    return new Promise((resolve, reject) => {
      const authenticationDetails = new AuthenticationDetails({
        Username: email,
        Password: password,
      });

      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool,
      });

      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: async (result) => {
          const token = result.getIdToken().getJwtToken();
          cognitoUser.getUserAttributes((err, attributes) => {
            if (err) {
              reject(err);
              return;
            }
            const userData = {};
            attributes.forEach((attr) => {
              userData[attr.Name] = attr.Value;
            });
            const userInfo = {
              username: cognitoUser.getUsername(),
              email: userData.email,
              name: userData.name || userData.email,
              ...userData,
            };
            setUser(userInfo);
            setIsAuthenticated(true);
            syncUserWithBackend(token);
            resolve(result);
          });
        },
        onFailure: (err) => {
          reject(err);
        },
      });
    });
  };

  const signUp = (email, password, name) => {
    return new Promise((resolve, reject) => {
      const attributeList = [
        new CognitoUserAttribute({
          Name: 'email',
          Value: email,
        }),
        new CognitoUserAttribute({
          Name: 'name',
          Value: name,
        }),
      ];

      userPool.signUp(email, password, attributeList, null, (err, result) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(result);
      });
    });
  };

  const confirmSignUp = (email, verificationCode) => {
    return new Promise((resolve, reject) => {
      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool,
      });

      cognitoUser.confirmRegistration(verificationCode, true, (err, result) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(result);
      });
    });
  };

  const signOut = () => {
    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.signOut();
    }
    localStorage.removeItem('user_id');
    setUser(null);
    setIsAuthenticated(false);
  };

  const getToken = () => {
    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser();
      if (!cognitoUser) {
        reject(new Error('No user found'));
        return;
      }
      cognitoUser.getSession((err, session) => {
        if (err || !session.isValid()) {
          reject(err || new Error('Invalid session'));
          return;
        }
        resolve(session.getIdToken().getJwtToken());
      });
    });
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    signIn,
    signUp,
    confirmSignUp,
    signOut,
    getToken,
    checkAuthState,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
