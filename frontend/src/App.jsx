import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import Discover from './pages/Discover';
import Collections from './pages/Collections';
import CollectionDetails from './pages/CollectionDetails';
import Chat from './pages/Chat';
import Profile from './pages/Profile';
import Groups from './pages/Groups';
import GroupRecommendations from './pages/GroupRecommendations';
import RestaurantDetails from './pages/RestaurantDetails';
import Friends from './pages/Friends';
import Login from './components/Login';
import Signup from './components/Signup';
import Navigation from './components/Navigation';
import './App.css';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('React Error:', error, errorInfo);
    console.error('Error stack:', error.stack);
    console.error('Error info:', errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '40px', 
          textAlign: 'center', 
          background: '#ff6b6b',
          color: 'white',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>❌ Something went wrong</h1>
          <p style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>{this.state.error?.toString()}</p>
          <pre style={{ 
            background: 'rgba(0,0,0,0.3)', 
            padding: '20px', 
            borderRadius: '8px',
            overflow: 'auto',
            maxWidth: '800px',
            textAlign: 'left'
          }}>
            {this.state.error?.stack}
          </pre>
          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              fontSize: '1rem',
              cursor: 'pointer',
              background: 'white',
              color: '#ff6b6b',
              border: 'none',
              borderRadius: '4px'
            }}
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    console.log('ProtectedRoute: Showing loading state');
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '24px',
        color: '#333',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        fontWeight: 'bold'
      }}>
        🔄 Loading... (Auth check in progress)
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
}

function AppRoutes() {
  console.log('AppRoutes: Calling useAuth hook...');
  const { isAuthenticated, loading } = useAuth();
  
  console.log('AppRoutes: isAuthenticated=', isAuthenticated, 'loading=', loading);
  console.log('AppRoutes: About to render routes, current path:', window.location.pathname);
  
  return (
    <div className="app">
      {isAuthenticated && <Navigation />}
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Discover />
            </ProtectedRoute>
          }
        />
        <Route
          path="/collections"
          element={
            <ProtectedRoute>
              <Collections />
            </ProtectedRoute>
          }
        />
        <Route
          path="/collections/:id"
          element={
            <ProtectedRoute>
              <CollectionDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/groups"
          element={
            <ProtectedRoute>
              <Groups />
            </ProtectedRoute>
          }
        />
        <Route
          path="/groups/:groupId/recommendations"
          element={
            <ProtectedRoute>
              <GroupRecommendations />
            </ProtectedRoute>
          }
        />
        <Route
          path="/restaurants/:id"
          element={
            <ProtectedRoute>
              <RestaurantDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="/friends"
          element={
            <ProtectedRoute>
              <Friends />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}

function App() {
  console.log('App component rendering...');
  console.log('App: Body computed styles:', window.getComputedStyle(document.body).background);
  
  try {
    return (
      <ErrorBoundary>
        <AuthProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </AuthProvider>
      </ErrorBoundary>
    );
  } catch (error) {
    throw error;
  }
}

export default App;
